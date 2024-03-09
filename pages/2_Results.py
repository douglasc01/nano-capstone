import streamlit as st
import datetime
from components import list_data_files, load_data, get_plot_data, get_lines, get_seconds


st.title("Results")

try:
    selected_files = st.multiselect(
        label="Select the data file(s) you would like to view",
        options=list_data_files(),
    )

    with st.expander(label="Chart options", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            normalized = st.toggle(label="Use normalized data", value=False)
            baseline = st.time_input(
                label="Select baseline range (minutes)",
                value=datetime.time(0, 2, 0),
                step=60,
            )
        with col2:
            moving_average = st.toggle(label="Use moving average", value=False)
            window = st.time_input(
                label="Select a moving average window (minutes)",
                value=datetime.time(0, 5, 0),
                step=60,
            )
        time_range = st.time_input(
            label="Select data range (hours-minutes)",
            value=datetime.time(2, 0, 0),
            step=300,
        )
        start_buffer = st.time_input(
            label="Select start buffer (minutes)", value=datetime.time(0, 0, 0), step=60
        )

    dataframes = {file: load_data(file) for file in selected_files}

    plot_dataframe = get_plot_data(
        dataframes=dataframes,
        data_range=get_seconds(time_range),
        start_buffer=get_seconds(start_buffer),
        normalized=normalized,
        baseline=get_seconds(baseline),
        moving_average=moving_average,
        window=get_seconds(window),
    )

    if selected_files:
        st.altair_chart(
            get_lines(
                plot_dataframe,
                normalized=normalized,
                title=(
                    "frequency versus time"
                    if not normalized
                    else "change in frequency versus time"
                ),
            ),
            theme="streamlit",
            use_container_width=True,
        )

except Exception as e:
    st.write(f"Error: {e}")
