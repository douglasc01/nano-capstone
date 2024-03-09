import datetime
import streamlit as st
import pandas as pd
import altair as alt
import os
import numpy as np


@st.cache_data
def get_seconds(time: datetime.time) -> int:
    return time.hour * 3600 + time.minute * 60 + time.second


def list_data_files() -> list[str]:
    data_files = os.listdir("data")
    return data_files


@st.cache_data
def load_data(file: str) -> pd.DataFrame:
    return pd.read_csv(f"data/{file}")


@st.cache_data
def get_plot_data(
    dataframes: dict[str, pd.DataFrame],
    data_range: int,
    start_buffer: int,
    normalized: bool,
    baseline: int,
    moving_average: bool,
    window: int,
) -> pd.DataFrame:
    merged_data = pd.DataFrame()

    for filename, dataframe in dataframes.items():
        updated_df = dataframe["freq"].rename(filename)[start_buffer:data_range]
        if normalized:
            updated_df = get_normalized_values(updated_df, baseline)
        if moving_average:
            updated_df = get_moving_average(updated_df, window)
        if len(dataframes) == 1:
            return pd.DataFrame(updated_df)
        merged_data = pd.concat([merged_data, updated_df], axis=1)

    return merged_data.reset_index(drop=True)


@st.cache_data
def get_baseline(data: pd.Series, n: int = 120) -> float:
    return np.average(data[0:n])


@st.cache_data
def get_normalized_values(data: pd.Series, baseline: int = 120) -> pd.Series:
    f0 = get_baseline(data, baseline)
    return (data / f0 - 1) * 100


@st.cache_data
def get_moving_average(data: pd.Series, window: int = 300) -> pd.Series:
    return data.rolling(window=window).mean().abs()


def get_lines(
    data: pd.DataFrame,
    title: str = "frequency versus time",
    normalized: bool = False,
    interactive: bool = True,
) -> alt.Chart:
    df_long = data.reset_index().melt(
        id_vars="index", var_name="legend", value_name="frequency"
    )
    df_long["time"] = pd.to_datetime(df_long["index"], unit="s")

    lines = (
        alt.Chart(df_long, title=title, height=500)
        .mark_line()
        .encode(
            x="utchoursminutesseconds(time):Q",
            y=alt.Y(
                "frequency:Q",
                scale=alt.Scale(
                    domain=(
                        [data.min().min() * 0.9, data.max().max() * 1.1]
                        if normalized
                        else [data.min().min() - 100, data.max().max() + 100]
                    )
                ),
                axis=alt.Axis(
                    title=(
                        "frequency (Hz)"
                        if not normalized
                        else "change in frequency (%)"
                    )
                ),
            ),
            color="legend",
        )
    )

    return lines.interactive() if interactive else lines
