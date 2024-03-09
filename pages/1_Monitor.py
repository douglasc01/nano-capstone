import serial
from serial.tools import list_ports

import streamlit as st
import pandas as pd

from components import get_lines
from datetime import datetime

import time


BAUD_RATES = [9600, 115200, 230400, 460800, 921600]


def list_serial_ports() -> list:
    ports = list_ports.comports()
    if not ports:
        return []
    else:
        return [port.device for port in ports]


def update_recording() -> None:
    st.session_state["recording"] = not st.session_state["recording"]


st.title("Monitor")

st.write("View and record real time sensor data")

if "monitor_data" not in st.session_state:
    st.session_state["monitor_data"] = pd.DataFrame(columns=["freq"])
if "selected_port" not in st.session_state:
    st.session_state["selected_port"] = None

try:
    col1, col2 = st.columns(2)
    with col1:
        selected_port = st.selectbox(
            label="Select the port the device is connected to",
            options=list_serial_ports(),
            key="selected_port",
            index=None,
        )
    with col2:
        baud_rate = st.selectbox(
            label="Select the baud rate for the device", options=BAUD_RATES, index=2
        )

    if st.button("Refresh ports"):
        list_serial_ports()

    if selected_port:
        ser = serial.Serial(selected_port, baud_rate)
        recording = st.session_state.get("recording")
        filename = st.session_state.get("filename")
        if recording and filename:
            file = open(f"data/{st.session_state.get('filename')}", "w")
            file.write("freq\n")

        current_datetime = datetime.now().strftime("%Y%m%d_%H:%M")
        formatted_filename = f"freq_data_{current_datetime}.txt"

        data = st.session_state["monitor_data"]

        monitor_col, recording_col, reset_col, filename_col = st.columns([1, 1, 1, 6])
        with monitor_col:
            running = st.toggle(label="Monitor", value=True)
        with recording_col:
            recording = st.toggle(label="Recording", key="recording")
        with reset_col:
            if st.button(label="Reset data"):
                ser.close()
                ser = serial.Serial(selected_port, baud_rate)
                st.session_state["monitor_data"] = pd.DataFrame(columns=["freq"])
                data = st.session_state["monitor_data"]
        with filename_col:
            filename_input = st.text_input(
                label="Filename", value=formatted_filename, key="filename"
            )

        placeholder = st.empty()

        with placeholder.container():
            while running:
                time.sleep(0.5)
                line = ser.readline().decode().strip()
                if "\r" in line:
                    continue
                data.loc[len(data)] = {"freq": int(line)}
                if recording:
                    file.write(line + "\n")
                    file.flush()
                with placeholder.container():
                    st.altair_chart(
                        get_lines(data), theme="streamlit", use_container_width=True
                    )
            st.session_state["monitor_data"] = data

        ser.close()

except Exception as e:
    st.write(f"Error: {e}")
