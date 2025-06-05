import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import itertools
import plotly.graph_objects as go
import plotly.io as pio
from scipy.interpolate import griddata
from statsmodels.tsa.filters.hp_filter import hpfilter
import os
import h5py
import json
import math

tick = pd.date_range("2018-1-1", "2021-12-31", freq="MS").strftime("%b%Y").tolist()


def debase(list):
    """
    De-bases the given time series list by subtracting the first value from all elements.

    """
    first_value = list[0]
    debased_list = [value - first_value for value in list]

    return debased_list


def cumulative_sum(time_series):
    """
    Calculates the cumulative sum of a time series.

    Parameters:
    - time_series: list or numpy array, the time series data

    Returns:
    - numpy array of cumulative sums
    """
    time_series = np.array(time_series)
    cumulative_values = np.cumsum(time_series)
    return cumulative_values


def normalize_value(data):
    base_list = [0] * len(data)
    return base_list


def percentage_change(base, compare):
    percentage_diff = [
        (b - a) / a * 100 if a != 0 else 0 for a, b in zip(base, compare)
    ]

    return percentage_diff


def group_average(df, column_name, group_column):
    """
    Calculate the average of the specified column for each group defined by the group_column in the DataFrame.
    """
    unique_groups = df[group_column].unique()
    group_averages = {}

    for group in unique_groups:
        group_data = df[df[group_column] == group]
        avg_values = calculate_average(group_data, column_name)
        group_averages[group] = avg_values

    return group_averages


import numpy as np


def clean_data(df, column_name):
    """
    Clean the specified column in the DataFrame by removing None values from the lists.
    """
    df[f"{column_name}_cleaned"] = df[column_name].apply(
        lambda value_list: [x for x in value_list if x is not None]
    )


def calculate_average(df, column_name):
    """
    Calculate the average of the specified column in the DataFrame across all lists at each time step.
    """
    max_length = max(
        len(value_list) for value_list in df[f"{column_name}_cleaned"]
    )  # Find the maximum length of the lists
    avg_values = [
        np.mean(
            [
                value_list[i]
                for value_list in df[f"{column_name}_cleaned"]
                if len(value_list) > i
            ]
        )
        for i in range(max_length)
    ]
    return avg_values


def calculate_confidence_interval(df, column_name, confidence=0.95):
    """
    Calculate the confidence interval for the specified column in the DataFrame across all lists at each time step.
    """
    max_length = max(len(value_list) for value_list in df[f"{column_name}_cleaned"])
    ci_lower = []
    ci_upper = []

    for i in range(max_length):
        values_at_t = [
            value_list[i]
            for value_list in df[f"{column_name}_cleaned"]
            if len(value_list) > i
        ]
        mean_at_t = np.mean(values_at_t)
        std_at_t = np.std(values_at_t)
        margin_of_error = 1.96 * std_at_t / np.sqrt(len(values_at_t))

        ci_lower.append(mean_at_t - margin_of_error)
        ci_upper.append(mean_at_t + margin_of_error)

    return ci_lower, ci_upper


def sensitivity_3d(
    name,
    data,
    length,
    covid_time,
    dataset_name,
    savecode,
    length_cut=10,
    area=False,
    export=False,
):

    # Note: data has to be a triplet of 3 series
    folder_path = r"Figures"  # saving folder

    # prepare data input
    x = []
    y = []
    z = data[2]

    for i in range(len(data[0])):
        x.append(data[0][i][-length:])
        x[i] = x[i][:length_cut]
        x[i] = np.array(x[i]).mean()

    for i in range(len(data[1])):
        y.append(data[1][i][-length:])
        y[i] = y[i][:length_cut]
        y[i] = np.array(y[i]).mean()

    x_min = np.min(x)
    x_max = np.max(x)
    y_min = np.min(y)
    y_max = np.max(y)

    xi = np.linspace(x_min, x_max, 900)
    yi = np.linspace(y_min, y_max, 900)

    X, Y = np.meshgrid(xi, yi)
    Z = griddata((x, y), z, (X, Y), method="cubic")

    fig = go.Figure()
    fig.add_trace(go.Surface(x=xi, y=yi, z=Z, colorscale="Cividis"))
    fig.update_layout(
        scene=dict(
            zaxis=dict(range=[0, 1]),
            xaxis_title=dataset_name[0],
            yaxis_title=dataset_name[1],
            zaxis_title=dataset_name[2],
        ),
        width=700,
        margin=dict(r=20, b=10, l=10, t=10),
    )

    fig.show()

    if export:
        # Export the plot as a PDF file in the 'figure' subfolder
        pio.write_image(
            fig,
            os.path.join(folder_path, savecode + "_" + str(name) + "_plot.pdf"),
            format="pdf",
        )


def scatter_3d(
    name, data, length, dataset_name, savecode, length_cut=10, area=False, export=False
):

    # Note: data has to be a triplet of 3 series
    folder_path = r"Figures"  # saving folder

    # prepare data input
    x = []
    y = []

    for i in range(len(data[0])):
        x.append(data[0][i])
        x[i] = x[i][-length:]
        if length_cut != None:
            x[i] = x[i][:length_cut]

    for i in range(len(data[0])):
        y.append(data[1][i])
        y[i] = y[i][-length:]
        if length_cut != None:
            y[i] = y[i][:length_cut]

    # Create a date range with the same length as each item in the variable list
    if length_cut != None:

        end_date = pd.to_datetime("2023-01-01")  # The given end date
        start_date = end_date - pd.DateOffset(
            months=length
        )  # Calculate the start date 48 months before
        date_range = pd.date_range(
            start=start_date, periods=length_cut, freq="MS"
        )  # Generate the date range
        ntick = length_cut

    else:
        date_range = pd.date_range(end="2023-01-01", periods=length, freq="MS")
        ntick = length
    print(date_range[0])

    fig = go.Figure()
    for i, item in enumerate(x):
        fig.add_trace(go.Scatter3d(x=date_range, y=y[i], z=x[i], name=dataset_name[i]))

    fig.show()

    if export:
        # Export the plot as a PDF file in the 'figure' subfolder
        pio.write_image(
            fig,
            os.path.join(folder_path, savecode + "_" + str(name) + "_plot.pdf"),
            format="pdf",
        )


def pline_plot(
    name,
    data,
    color_set,
    length,
    covid_time,
    dataset_name,
    savecode,
    graph_title,
    length_cut=None,
    tick=3,
    area=False,
    export=False,
    is_percentage=False,
    apply_hp_filter=False,
    hp_lambda=14400,
):
    folder_path = r"Figures"  # Saving folder
    x = []

    # Prepare data input
    for i in range(len(data)):
        x.append(data[i])
        x[i] = x[i][-length:]

        if length_cut is not None:
            x[i] = x[i][:length_cut]

    # Apply Hodrick-Prescott filter if selected
    if apply_hp_filter:
        for i in range(len(x)):
            cycle, trend = hpfilter(x[i], lamb=hp_lambda)
            x[i] = trend  # Replace the original data with the trend component

    # Create a date range with the same length as each item in the variable list
    if length_cut is not None:
        end_date = pd.to_datetime("2025-01-01")  # The given end date
        start_date = end_date - pd.DateOffset(
            months=length
        )  # Calculate the start date 48 months before
        date_range = pd.date_range(
            start=start_date, periods=length_cut, freq="MS"
        )  # Generate the date range
    else:
        date_range = pd.date_range(end="2025-01-01", periods=length, freq="MS")

    # Create tick values for every three months
    tickvals = date_range[::tick]
    ticktext = [date.strftime("%m/%y") for date in tickvals]

    fig = go.Figure()
    for i, item in enumerate(x):
        fig.add_trace(
            go.Scatter(
                x=date_range,
                y=item,
                name=dataset_name[i],
                mode="lines",
                marker=dict(color=color_set[i]),
            )
        )

    # Set the y-axis label depending on whether it's percentage or absolute numbers
    y_axis_title = f"{name} (%)" if is_percentage else name

    # Set the x-axis title, y-axis title, and chart title
    fig.update_layout(
        xaxis=dict(
            tickmode="array",
            tickvals=tickvals,
            ticktext=ticktext,
            tickangle=-90,
            tickwidth=2,
            ticklen=10,
            gridcolor="darkgray",
            zerolinecolor="darkgray",
            gridwidth=0.1,
            ticks="outside",
            tickfont=dict(size=15),
            showline=True,
            linewidth=2,
            linecolor="black",
            mirror=True,
            fixedrange=True,
        ),
        yaxis=dict(
            title=dict(
                text=y_axis_title,
                font=dict(family="Times New Roman, serif", size=20, color="black"),
            ),
            tickwidth=2,
            ticklen=10,
            gridcolor="lightgray",
            zerolinecolor="lightgray",
            gridwidth=0.1,
            ticks="outside",
            tickfont=dict(size=15),
            showline=True,
            linewidth=2,
            linecolor="black",
            mirror=True,
            fixedrange=True,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="left",
            x=0,
            font=dict(size=16),
        ),
        # Show a gray grid on the plot
        yaxis_gridcolor="darkgray",
        xaxis_gridcolor="darkgray",
        plot_bgcolor="white",
        margin=dict(l=50, r=20, t=50, b=50, pad=4),
        height=700,
        width=700,
        title=dict(
            text=graph_title,
            x=0.5,
            y=0.99,
            xanchor="center",
            yanchor="top",
            font=dict(family="Times New Roman, serif", size=36, color="black"),
        ),
    )
    # Add pre-covid area
    if area:
        fig.add_vline(x=covid_time, line_width=4, line_dash="dash", line_color="red")
    # Option to export the graph
    if export:
        # Export the plot as a PDF file in the 'figure' subfolder
        pio.write_image(
            fig,
            os.path.join(folder_path, savecode + "_" + str(name) + "_plot.pdf"),
            format="pdf",
        )

    fig.show()


def pline_plot_with_ci(
    name,
    data,
    color_set,
    length,
    covid_time,
    dataset_name,
    savecode,
    graph_title,
    ci_data,
    length_cut=None,
    tick=3,
    area=False,
    export=False,
):
    """
    A function to plot time series data with optional confidence intervals and pre-COVID vertical line.

    Parameters:
    - name: str, name of the y-axis (e.g., 'GDP')
    - data: list of numpy arrays, each containing the time series data
    - color_set: list of colors, to be used for each dataset
    - length: int, the length of the time series data to consider
    - covid_time: datetime, the time of the COVID onset for the vertical line
    - dataset_name: list of strings, names of the datasets for the legend
    - savecode: str, the name to use when saving the figure
    - graph_title: str, the title of the graph
    - ci_data: list of tuples, each containing (lower_bound, upper_bound) arrays for confidence intervals
    - length_cut: int, optional, if provided, the time series data is truncated to this length
    - area: bool, optional, if True, adds a vertical line at covid_time
    - export: bool, optional, if True, exports the figure as a PDF
    """

    folder_path = r"Figures"  # saving folder
    x = []
    ci_lower = []
    ci_upper = []

    # Prepare data and confidence interval input
    for i in range(len(data)):
        x.append(data[i][-length:])
        if length_cut is not None:
            x[i] = x[i][:length_cut]

        lower_bound, upper_bound = ci_data[i]
        ci_lower.append(lower_bound[-length:])
        ci_upper.append(upper_bound[-length:])

        if length_cut is not None:
            ci_lower[i] = ci_lower[i][:length_cut]
            ci_upper[i] = ci_upper[i][:length_cut]

    # Create a date range with the same length as each item in the variable list
    if length_cut is not None:
        end_date = pd.to_datetime("2023-01-01")  # The given end date
        start_date = end_date - pd.DateOffset(
            months=length
        )  # Calculate the start date months before
        date_range = pd.date_range(
            start=start_date, periods=length_cut, freq="MS"
        )  # Generate the date range
        ntick = length_cut
    else:
        date_range = pd.date_range(end="2023-01-01", periods=length, freq="MS")
        ntick = length

    # Create tick values for every three months
    tickvals = date_range[::tick]
    ticktext = [date.strftime("%m/%y") for date in tickvals]

    fig = go.Figure()

    for i, item in enumerate(x):
        # Add the line for the data
        fig.add_trace(
            go.Scatter(
                x=date_range,
                y=item,
                name=dataset_name[i],
                mode="lines",
                marker=dict(color=color_set[i]),
            )
        )

        # Add the confidence interval band
        fig.add_trace(
            go.Scatter(
                x=np.concatenate([date_range, date_range[::-1]]),
                y=np.concatenate([ci_upper[i], ci_lower[i][::-1]]),
                fill="toself",
                fillcolor=color_set[i].replace("rgb", "rgba").replace(")", ", 0.2)"),
                line=dict(color="rgba(255,255,255,0)"),
                showlegend=False,
                name=f"{dataset_name[i]} CI",
            )
        )

    # Set the x-axis title, y-axis title, and chart title
    fig.update_layout(
        xaxis=dict(
            tickmode="array",
            tickvals=tickvals,
            ticktext=ticktext,
            tickangle=-90,
            tickwidth=2,
            ticklen=10,
            gridcolor="darkgray",
            zerolinecolor="darkgray",
            gridwidth=0.1,
            ticks="outside",
            tickfont=dict(size=15),
            showline=True,
            linewidth=2,
            linecolor="black",
            mirror=True,
            fixedrange=True,
        ),
        yaxis=dict(
            title=dict(
                text=name,
                font=dict(family="Times New Roman, serif", size=20, color="black"),
            ),
            tickwidth=2,
            ticklen=10,
            gridcolor="lightgray",
            zerolinecolor="lightgray",
            gridwidth=0.1,
            ticks="outside",
            tickfont=dict(size=15),
            showline=True,
            linewidth=2,
            linecolor="black",
            mirror=True,
            fixedrange=True,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="left",
            x=0,
            font=dict(size=16),
        ),
        yaxis_gridcolor="darkgray",
        xaxis_gridcolor="darkgray",
        plot_bgcolor="white",
        margin=dict(l=50, r=20, t=50, b=50, pad=4),
        height=700,
        width=700,
        title=dict(
            text=graph_title,
            x=0.5,
            y=0.99,
            xanchor="center",
            yanchor="top",
            font=dict(family="Times New Roman, serif", size=36, color="black"),
        ),
    )

    # Add pre-covid area
    if area:
        fig.add_vline(x=covid_time, line_width=4, line_dash="dash", line_color="red")

    if export:
        # Export the plot as a PDF file in the 'figure' subfolder
        pio.write_image(
            fig,
            os.path.join(folder_path, savecode + "_" + str(name) + "_plot.pdf"),
            format="pdf",
        )

    fig.show()


def pbar_plot(
    name, data, length, covid_time, dataset_name, savecode, area=False, export=False
):

    folder_path = "figures"  # Generic figures directory
    x = []
    for i in range(len(data)):
        x.append(data[i])
        x[i] = x[i][-length:]

    # Flatten the list of lists x into a 1D array
    flat_x = list(itertools.chain.from_iterable(x))

    # Calculate the maximum value of flat_x
    max_value = np.max(flat_x)
    min_value = np.min(flat_x)
    # Create a date range with the same length as each item in the variable list
    date_range = pd.date_range(end="2020-12-31", periods=length, freq="MS")

    # Create tick values for every three months
    tickvals = date_range[::3]
    ticktext = [date.strftime("%m/%y") for date in tickvals]

    fig = go.Figure()
    for i, item in enumerate(x):
        fig.add_trace(go.Bar(x=date_range, y=item, name=name + "_" + dataset_name[i]))

    # Set the x-axis title, y-axis title, and chart title
    fig.update_layout(
        xaxis=dict(
            title=dict(
                text="Comparison Plot",
                font=dict(family="Times New Roman, serif", size=20, color="black"),
            ),
            tickmode="array",
            tickvals=tickvals,
            ticktext=ticktext,
            tickangle=-90,
            tickwidth=2,
            ticklen=10,
            gridcolor="darkgray",
            zerolinecolor="darkgray",
            gridwidth=0.1,
            ticks="outside",
            tickfont=dict(size=15),
            showline=True,
            linewidth=2,
            linecolor="black",
            mirror=True,
            fixedrange=True,
        ),
        yaxis=dict(
            tickwidth=2,
            ticklen=10,
            gridcolor="lightgray",
            zerolinecolor="lightgray",
            gridwidth=0.1,
            ticks="outside",
            tickfont=dict(size=15),
            showline=True,
            linewidth=2,
            linecolor="black",
            mirror=True,
            fixedrange=True,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.3,
            xanchor="left",
            x=0,
        ),
        # Show a gray grid on the plot
        yaxis_gridcolor="darkgray",
        xaxis_gridcolor="darkgray",
        plot_bgcolor="white",
        margin=dict(l=50, r=20, t=50, b=50, pad=4),
        height=600,
        width=1000,
    )
    # Add pre-covid area
    if area:
        fig.add_shape(
            type="line",
            x0=covid_time,
            x1=covid_time,
            y0=min_value,
            y1=max_value,
            line=dict(
                color="red",
                width=4,
            ),
        )
        fig.add_vrect(
            x0=pd.to_datetime(date_range[0]),
            x1=pd.to_datetime(covid_time),
            annotation_text="Pre-Pandemic",
            annotation_position="top left",
            annotation=dict(font_size=20, font_family="Times New Roman"),
            fillcolor="lightgreen",
            opacity=0.25,
            line_width=0,
        )
    if export:
        # Export the plot as a PDF file in the 'figure' subfolder
        pio.write_image(
            fig,
            os.path.join(folder_path, str(name) + "_" + savecode + "_plot.pdf"),
            format="pdf",
        )

    fig.show()


def pradar_plot(
    name,
    data,
    length,
    covid_time,
):
    # Create a date range with the same length as each item in the variable list
    date_range = pd.date_range(end="2010-12-31", periods=length, freq="MS")

    data = data[-length:]

    # Choose the date closest to the covid_time and retrieve the corresponding data
    covid_timestamp = pd.Timestamp(covid_time)
    closest_date = date_range[abs(date_range - covid_timestamp).argmin()]
    data_snapshot = [
        data[i][date_range == closest_date].values[0] for i in range(len(data))
    ]

    # Plot the data using a radar chart
    categories = [name + "_" + str(i + 1) for i in range(len(data))]
    fig = go.Figure(
        go.Radar(
            categories=categories,
            values=data_snapshot,
            line=dict(color="red"),
        )
    )

    fig.update_layout(
        title={
            "text": name,
            "font": {"size": 24},
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
        },
        xaxis_title="Category",
        yaxis_title="Value",
    )
    fig.show()


def covline_plot(
    name,
    data,
    color_set,
    length,
    dataset_name,
    savecode,
    graph_title,
    tick=3,
    export=False,
):

    folder_path = "figures"  # Generic figures directory
    x = []
    for i in range(len(data)):
        x.append(data[i])
        x[i] = x[i][0:length]

    # Flatten the list of lists x into a 1D array
    flat_x = list(itertools.chain.from_iterable(x))

    # Calculate the maximum value of flat_x
    max_value = np.max(flat_x)
    min_value = np.min(flat_x)

    # Create a date range with the same length as each item in the variable list
    date_range = pd.date_range(start="2020-01-01", periods=length, freq="D")

    # Create tick values for every three months
    tickvals = date_range[::tick]
    ticktext = [date.strftime("%m/%y") for date in tickvals]

    fig = go.Figure()
    for i, item in enumerate(x):
        fig.add_trace(
            go.Scatter(
                x=date_range,
                y=item,
                name=name + "_" + dataset_name[i],
                mode="lines",
                marker=dict(color=color_set[i]),
            )
        )

    # Set the x-axis title, y-axis title, and chart title
    fig.update_layout(
        xaxis=dict(
            tickmode="array",
            tickvals=tickvals,
            ticktext=ticktext,
            tickangle=-90,
            tickwidth=3,
            ticklen=10,
            gridcolor="darkgray",
            zerolinecolor="darkgray",
            gridwidth=0.1,
            ticks="outside",
            tickfont=dict(size=15),
            showline=True,
            linewidth=2,
            linecolor="black",
            mirror=True,
            fixedrange=True,
        ),
        yaxis=dict(
            tickwidth=2,
            ticklen=10,
            title=dict(
                text=name,
                font=dict(family="Times New Roman, serif", size=20, color="black"),
            ),
            gridcolor="lightgray",
            zerolinecolor="lightgray",
            gridwidth=1,
            ticks="outside",
            tickfont=dict(size=15),
            showline=True,
            linewidth=2,
            linecolor="black",
            mirror=True,
            fixedrange=True,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="left",
            x=0,
            font=dict(size=12),
        ),
        # Show a gray grid on the plot
        # yaxis_gridcolor='darkgray',
        # xaxis_gridcolor='darkgray',
        plot_bgcolor="white",
        margin=dict(l=50, r=20, t=50, b=50, pad=4),
        height=700,
        width=700,
        title=dict(
            text=graph_title,
            x=0.5,
            y=0.99,
            xanchor="center",
            yanchor="top",
            font=dict(family="Times New Roman, serif", size=36, color="black"),
        ),
    )
    if export:
        # Export the plot as a PDF file in the 'figure' subfolder
        pio.write_image(
            fig,
            os.path.join(folder_path, savecode + "_" + str(name) + "_plot.pdf"),
            format="pdf",
        )

    fig.show()


def box_plot(
    name,
    data,
    color_set,
    length,
    dataset_name,
    savecode,
    graph_title,
    length_cut=None,
    export=False,
):

    folder_path = r"Figures"  # saving folder
    x = []

    # prepare data input
    for i in range(len(data)):
        x.append(data[i])
        x[i] = x[i][-length:]

        if length_cut != None:
            x[i] = x[i][:length_cut]

    fig = go.Figure()
    for i, item in enumerate(x):
        fig.add_trace(
            go.Box(y=item, name=dataset_name[i], marker=dict(color=color_set[i]))
        )

    # Set the x-axis title, y-axis title, and chart title

    fig.update_layout(
        xaxis=dict(
            showline=True,
            linecolor="black",
            linewidth=2,
            gridcolor="darkgray",
            ticks="outside",
            tickfont=dict(size=10),
            mirror=True,
        ),
        yaxis=dict(
            tickwidth=2,
            ticklen=10,
            title=dict(
                text=name,
                font=dict(family="Times New Roman, serif", size=20, color="black"),
            ),
            gridcolor="lightgray",
            zerolinecolor="lightgray",
            gridwidth=0.1,
            ticks="outside",
            tickfont=dict(size=15),
            showline=True,
            linewidth=2,
            linecolor="black",
            mirror=True,
            fixedrange=True,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.1,
            xanchor="left",
            x=0,
            font=dict(size=16),
        ),
        # Show a gray grid on the plot
        yaxis_gridcolor="darkgray",
        xaxis_gridcolor="darkgray",
        plot_bgcolor="white",
        margin=dict(l=50, r=20, t=50, b=50, pad=4),
        height=700,
        width=700,
        title=dict(
            text=graph_title,
            x=0.5,
            y=0.99,
            xanchor="center",
            yanchor="top",
            font=dict(family="Times New Roman, serif", size=36, color="black"),
        ),
    )

    if export:
        # Export the plot as a PDF file in the 'figure' subfolder
        pio.write_image(
            fig,
            os.path.join(folder_path, savecode + "_" + str(name) + "_plot.pdf"),
            format="pdf",
        )

    fig.show()


def heatmap_plot(
    name,
    data,
    color_set,
    length,
    dataset_names,
    savecode,
    graph_title,
    length_cut=None,
    tick=3,
    export=False,
):
    folder_path = "Figures"  # Saving folder

    # Validate inputs
    if len(data) == 0:
        raise ValueError("Data list is empty")

    num_datasets = len(data)
    dates = pd.date_range(end="2023-01-01", periods=length, freq="MS")

    # Create a DataFrame for the heatmap
    heatmap_data = np.zeros((num_datasets, length))

    # Prepare and truncate data if length_cut is provided
    for i, dataset in enumerate(data):
        if length_cut is not None:
            heatmap_data[i, :length_cut] = dataset[:length_cut]
        else:
            heatmap_data[i, : len(dataset)] = dataset

    # Create the heatmap
    fig = go.Figure()

    # Create heatmap
    heatmap = go.Heatmap(
        z=heatmap_data,
        x=dates,
        y=dataset_names,
        colorscale=color_set,
        colorbar=dict(title=name),
        zmin=np.nanmin(heatmap_data),  # Min value for color scale
        zmax=np.nanmax(heatmap_data),  # Max value for color scale
        showscale=True,
    )
    fig.add_trace(heatmap)

    # Add separator lines between scenarios
    for i in range(1, num_datasets):
        fig.add_shape(
            type="line",
            x0=dates[0],
            x1=dates[-1],
            y0=i - 0.5,
            y1=i - 0.5,
            line=dict(color="black", width=2),
        )

    # Update layout
    fig.update_layout(
        title=dict(
            text=graph_title,
            x=0.5,
            y=0.99,
            xanchor="center",
            yanchor="top",
            font=dict(family="Times New Roman, serif", size=36, color="black"),
        ),
        xaxis=dict(
            title="Date",
            tickmode="array",
            tickvals=dates[::tick],
            ticktext=[date.strftime("%m/%y") for date in dates[::tick]],
            tickangle=-90,
            tickwidth=2,
            ticklen=10,
            gridcolor="darkgray",
            zerolinecolor="darkgray",
            gridwidth=0.1,
            ticks="outside",
            tickfont=dict(size=15),
            showline=True,
            linewidth=2,
            linecolor="black",
            mirror=True,
            fixedrange=True,
        ),
        yaxis=dict(
            title=dict(
                text=name,
                font=dict(family="Times New Roman, serif", size=20, color="black"),
            ),
            tickwidth=2,
            ticklen=10,
            gridcolor="lightgray",
            zerolinecolor="lightgray",
            gridwidth=0.1,
            ticks="outside",
            tickfont=dict(size=15),
            showline=True,
            linewidth=2,
            linecolor="black",
            mirror=True,
            fixedrange=True,
        ),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=50, r=20, t=50, b=50, pad=4),
        height=700,
        width=1000,
    )

    # Export the plot if required
    if export:
        pio.write_image(
            fig, os.path.join(folder_path, savecode + "_heatmap.pdf"), format="pdf"
        )

    fig.show()
