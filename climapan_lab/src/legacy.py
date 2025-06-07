"""Compatibility helpers for migrating from AgentPy to JaxABM."""

import jaxabm.agentpy as ap
import numpy as np
from .param_dict import ParamDict


class AgentList(ap.AgentList):
    """AgentList with list-style indexing for backward compatibility.

    The original AgentPy library created Python agent objects during ``setup``
    so that they could be accessed and modified before the simulation run.  In
    JaxABM, agent states are initialised lazily when ``Model.initialize`` is
    called.  This wrapper therefore constructs lightweight agent instances on
    creation and stores them in ``_agent_cache`` so that tests expecting the
    AgentPy behaviour continue to work.
    """

    def __init__(self, model, n, agent_class, **kwargs):
        params = kwargs or dict(getattr(model, "p", {}))
        super().__init__(model, n, agent_class, **params)
        # Ensure underlying agent wrapper uses attribute access
        if hasattr(self, "agent_type"):
            self.agent_type.agent_instance.p = ParamDict(dict(params))
            self.agent_type.agent_instance.model = model
        self._agent_cache = []
        for i in range(self.n):
            a = self.agent_class()
            a.model = self.model
            a.id = i
            base_params = self.params if self.params else getattr(self.model, "p", {})
            a.p = ParamDict(dict(base_params))
            a._state = {}
            self._agent_cache.append(a)
        # Register with the model for state updates, emulating Model.add_agents
        if hasattr(self.model, "_agent_lists"):
            name = getattr(self, "name", None)
            if not name:
                name = self.agent_class.__name__.lower() + "s"
            self.model._agent_lists[name] = self
            self.name = name
            self.model._agent_instances[name] = list(self._agent_cache)
            # Include template agent so that attribute assignments during
            # initialization update its local state correctly
            self.model._agent_instances[name].append(self.agent_type.agent_instance)

        # After registration, call setup on each agent so that state-setting
        # logic can safely use the model's update hooks.
        for a in self._agent_cache:
            init_state = a.setup()
            if isinstance(init_state, dict):
                a._state.update(init_state)


    def _get_state_at(self, index):
        """Return a dictionary of state values for the agent at ``index``."""
        # Access states directly from the underlying collection to avoid
        # triggering property lookups that expect a fully initialized model.
        states = self.collection.states
        if not states:
            return self._agent_cache[index]._state
        return {k: v[index] for k, v in states.items()}

    def __getitem__(self, index):
        """Return a temporary agent object at ``index``.

        JaxABM's :class:`AgentCollection` does not support subscripting, so
        we recreate an :class:`Agent` instance using the stored states.  This
        mimics the old AgentPy behaviour that tests rely on.
        """
        if index >= len(self._agent_cache):
            raise IndexError("Agent index out of range")
        agent = self._agent_cache[index]
        states = self.collection.states
        if states:
            agent._state = self._get_state_at(index)
        return agent

    def __setitem__(self, index, value):
        """Assign a complete state dictionary to the agent at ``index``."""
        if not hasattr(value, "_state"):
            raise ValueError("Value must be an Agent with '_state' attribute")
        states = self.collection.states
        if states:
            for k in states:
                states[k] = states[k].at[index].set(value._state.get(k, states[k][index]))
        if index < len(self._agent_cache):
            self._agent_cache[index] = value

    def __add__(self, other):
        if isinstance(other, AgentList):
            return self._agent_cache + other._agent_cache
        return NotImplemented

    def __radd__(self, other):
        if isinstance(other, list):
            return other + self._agent_cache
        return NotImplemented

    # ------------------------------------------------------------------
    # Compatibility helpers replicating AgentPy AgentList behaviour
    # ------------------------------------------------------------------
    def getCovidStateAttr(self, attr):
        """Return an array of covid state attributes for all agents."""
        return np.array([a.getCovidStateAttr(attr) for a in self._agent_cache])

    def isDead(self):
        """Return boolean array whether each agent is dead."""
        return np.array([a.isDead() for a in self._agent_cache])

    def isEmployed(self):
        """Return boolean array whether each agent is employed."""
        return np.array([a.isEmployed() for a in self._agent_cache])

    def select(self, condition):
        """Select agents by boolean mask or callable condition."""
        if callable(condition):
            return super().select(condition)
        mask = np.array(condition)
        filtered_count = int(np.sum(mask))
        filtered = AgentList(self.model, filtered_count, self.agent_class, **self.params)
        if hasattr(self.collection, 'states') and self.collection.states is not None:
            if hasattr(self.collection, 'filter'):
                filtered.collection = self.collection.filter(lambda s: mask)
        # keep cache consistent
        filtered._agent_cache = [a for a, m in zip(self._agent_cache, mask) if m]
        return filtered

    def __iter__(self):
        """Iterate over cached agent instances only."""
        return iter(self._agent_cache)

    def __getattr__(self, name):
        """Delegate unknown attribute access to underlying agents."""
        states = getattr(self.collection, 'states', None)
        if states is not None and name in states:
            return super().__getattr__(name)
        if hasattr(self.agent_class, name):
            def aggregator(*args, **kwargs):
                return np.array([
                    getattr(a, name)(*args, **kwargs) for a in self._agent_cache
                ])
            return aggregator
        if self._agent_cache and hasattr(self._agent_cache[0], name):
            return [getattr(a, name) for a in self._agent_cache]
        return super().__getattr__(name)
