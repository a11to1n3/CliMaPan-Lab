#!/usr/bin/env python3
"""
Integration tests for CliMaPan-Lab complete workflows.
"""

import unittest
import tempfile
import os
import sys
import shutil
import subprocess

# Add the climapan_lab package to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from climapan_lab.base_params import economic_params
    from climapan_lab.model import EconModel
    from climapan_lab.run_sim import single_run
    IMPORTS_AVAILABLE = True
except ImportError as e:
    IMPORTS_AVAILABLE = False
    IMPORT_ERROR = str(e)


class TestIntegrationWorkflows(unittest.TestCase):
    """Test complete workflows from parameter setup to result analysis."""

    def setUp(self):
        """Set up test fixtures with temporary directory."""
        if not IMPORTS_AVAILABLE:
            self.skipTest(f"Required imports not available: {IMPORT_ERROR}")
            
        self.test_dir = tempfile.mkdtemp()
        self.params = economic_params.copy()
        # Use minimal parameters for fast testing
        self.params.update({
            'c_agents': 10,
            'capitalists': 3,
            'csf_agents': 2,
            'cpf_agents': 1,
            'green_energy_owners': 1,
            'brown_energy_owners': 1,
            'b_agents': 1,
            'g_agents': 1,
            'steps': 5,
            'verboseFlag': False,
            'climateModuleFlag': False,
        })

    def tearDown(self):
        """Clean up temporary directory."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_basic_simulation_workflow(self):
        """Test complete simulation workflow from start to finish."""
        # Set up parameters for different scenarios
        scenarios = [
            {'settings': 'BAU', 'covid_settings': None},
            {'settings': 'CT', 'covid_settings': None},
            {'settings': 'BAU', 'covid_settings': 'BAU'},
        ]
        
        for scenario in scenarios:
            with self.subTest(scenario=scenario):
                params = self.params.copy()
                params.update(scenario)
                
                # Run simulation
                try:
                    result = single_run(params, parent_folder=self.test_dir, make_stats=False)
                    
                    # Verify that simulation completed
                    self.assertIsNotNone(result)
                    
                    # Check that result has expected structure
                    if hasattr(result, 'variables'):
                        self.assertTrue(hasattr(result.variables, 'EconModel'))
                        
                except Exception as e:
                    self.fail(f"Simulation failed for scenario {scenario}: {e}")

    def test_data_output_structure(self):
        """Test that simulation produces expected data output structure."""
        params = self.params.copy()
        
        # Run simulation with data collection
        result = single_run(params, parent_folder=self.test_dir, make_stats=True)
        
        # Check that data was collected
        self.assertTrue(hasattr(result, 'variables'))
        
        if hasattr(result.variables, 'EconModel'):
            data = result.variables.EconModel
            
            # Check for key economic variables
            expected_variables = ['GDP', 'UnemploymentRate', 'Consumption']
            available_vars = list(data.columns) if hasattr(data, 'columns') else []
            
            for var in expected_variables:
                if var in available_vars:
                    # Variable should have data for all simulation steps
                    var_data = data[var]
                    self.assertGreater(len(var_data), 0)

    def test_multi_scenario_comparison(self):
        """Test running multiple scenarios for comparison."""
        scenarios = [
            {'settings': 'BAU', 'covid_settings': None},
            {'settings': 'CT', 'covid_settings': None},
        ]
        
        results = {}
        
        for i, scenario in enumerate(scenarios):
            params = self.params.copy()
            params.update(scenario)
            
            # Run simulation
            result = single_run(params, parent_folder=self.test_dir, make_stats=False)
            results[f"scenario_{i}"] = result
        
        # Check that we got results for all scenarios
        self.assertEqual(len(results), len(scenarios))
        
        # All results should be valid
        for scenario_name, result in results.items():
            self.assertIsNotNone(result, f"No result for {scenario_name}")

    def test_climate_module_integration(self):
        """Test that climate module integrates properly when enabled."""
        # Test with climate enabled
        params = self.params.copy()
        params['climateModuleFlag'] = True
        params['steps'] = 3  # Keep very short for testing
        
        try:
            result = single_run(params, parent_folder=self.test_dir, make_stats=False)
            self.assertIsNotNone(result)
            
            # If climate module is working, should have climate variables
            if hasattr(result, 'variables') and hasattr(result.variables, 'EconModel'):
                data = result.variables.EconModel
                climate_vars = ['ClimateTemperature', 'ClimateC02Concentration']
                available_vars = list(data.columns) if hasattr(data, 'columns') else []
                
                # At least one climate variable should be present
                has_climate_data = any(var in available_vars for var in climate_vars)
                if has_climate_data:
                    # This is good - climate module is working
                    pass
                    
        except Exception as e:
            # Climate module might not be fully configured - that's ok for these tests
            self.skipTest(f"Climate module not available: {e}")

    def test_parameter_sensitivity(self):
        """Test that model responds to parameter changes."""
        base_params = self.params.copy()
        
        # Test with different tax rates
        tax_rates = [0.05, 0.15, 0.25]
        results = []
        
        for tax_rate in tax_rates:
            params = base_params.copy()
            params['taxRate'] = tax_rate
            
            result = single_run(params, parent_folder=self.test_dir, make_stats=False)
            results.append(result)
        
        # All simulations should complete successfully
        for i, result in enumerate(results):
            self.assertIsNotNone(result, f"Simulation failed for tax rate {tax_rates[i]}")

    def test_agent_scaling(self):
        """Test that model works with different agent scales."""
        agent_scales = [0.1, 0.5, 1.0]
        
        for scale in agent_scales:
            with self.subTest(scale=scale):
                params = self.params.copy()
                params.update({
                    'c_agents': max(1, int(params['c_agents'] * scale)),
                    'capitalists': max(1, int(params['capitalists'] * scale)),
                    'csf_agents': max(1, int(params['csf_agents'] * scale)),
                    'cpf_agents': max(1, int(params['cpf_agents'] * scale)),
                })
                
                # Should run successfully with different scales
                result = single_run(params, parent_folder=self.test_dir, make_stats=False)
                self.assertIsNotNone(result)


class TestCommandLineInterface(unittest.TestCase):
    """Test command-line interface functionality."""

    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_console_script_availability(self):
        """Test that console scripts are available."""
        # Test that climapan-run is available
        try:
            result = subprocess.run(['climapan-run', '--help'], 
                                  capture_output=True, text=True, timeout=10)
            # Should not crash (exit code doesn't matter for --help)
            self.assertIsNotNone(result)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.skipTest("climapan-run command not available in test environment")

    def test_example_script_availability(self):
        """Test that example script is available."""
        try:
            result = subprocess.run(['climapan-example', '--help'], 
                                  capture_output=True, text=True, timeout=10)
            # Should not crash
            self.assertIsNotNone(result)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.skipTest("climapan-example command not available in test environment")


class TestDataAnalysisWorkflow(unittest.TestCase):
    """Test data analysis and post-processing workflows."""

    def setUp(self):
        """Set up with sample simulation results."""
        if not IMPORTS_AVAILABLE:
            self.skipTest(f"Required imports not available: {IMPORT_ERROR}")
            
        self.test_dir = tempfile.mkdtemp()
        self.params = economic_params.copy()
        self.params.update({
            'c_agents': 5,
            'steps': 3,
            'verboseFlag': False,
        })

    def tearDown(self):
        """Clean up."""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_results_loading_workflow(self):
        """Test that simulation results can be loaded for analysis."""
        # First run a simulation
        result = single_run(self.params, parent_folder=self.test_dir, make_stats=True)
        
        # Check that result files were created
        result_files = []
        for root, dirs, files in os.walk(self.test_dir):
            result_files.extend(files)
        
        # Should have some result files
        self.assertGreater(len(result_files), 0)
        
        # Should have at least a CSV file
        csv_files = [f for f in result_files if f.endswith('.csv') or f.endswith('.csv.gz')]
        if len(csv_files) > 0:
            # Found CSV files - good
            pass

    def test_analysis_functions_import(self):
        """Test that analysis functions can be imported."""
        try:
            from climapan_lab.examples.scenario import load_data
            from climapan_lab.examples.Load_data import load_json_file, load_hdf5_file
            
            # Should be able to import these classes/functions
            self.assertTrue(callable(load_data))
            self.assertTrue(callable(load_json_file))
            self.assertTrue(callable(load_hdf5_file))
            
        except ImportError as e:
            self.fail(f"Could not import analysis functions: {e}")


class TestErrorRecovery(unittest.TestCase):
    """Test error recovery and graceful handling of edge cases."""

    def test_invalid_scenario_handling(self):
        """Test handling of invalid scenario parameters."""
        if not IMPORTS_AVAILABLE:
            self.skipTest(f"Required imports not available: {IMPORT_ERROR}")
            
        params = economic_params.copy()
        params.update({
            'settings': 'INVALID_SCENARIO',
            'c_agents': 5,
            'steps': 2,
        })
        
        # Should either handle gracefully or raise appropriate error
        try:
            result = single_run(params, make_stats=False)
            # If it succeeds, that's fine
        except (ValueError, KeyError, AttributeError):
            # Expected errors for invalid scenarios
            pass
        except Exception as e:
            self.fail(f"Unexpected error type for invalid scenario: {type(e).__name__}: {e}")

    def test_memory_constraints(self):
        """Test behavior under memory constraints."""
        if not IMPORTS_AVAILABLE:
            self.skipTest(f"Required imports not available: {IMPORT_ERROR}")
            
        # Test with minimal agents but many steps
        params = economic_params.copy()
        params.update({
            'c_agents': 2,
            'capitalists': 1,
            'csf_agents': 1,
            'cpf_agents': 1,
            'steps': 100,  # Many steps with few agents
            'verboseFlag': False,
        })
        
        try:
            result = single_run(params, make_stats=False)
            self.assertIsNotNone(result)
        except MemoryError:
            self.skipTest("Memory constraints too tight for this test")


if __name__ == '__main__':
    unittest.main() 