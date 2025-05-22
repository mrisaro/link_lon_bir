import pandas as pd
import os
import re
import allantools
import matplotlib.pyplot as plt
from datetime import timedelta


def load_frequency_data(filepath):
    """
    Loads frequency data from the given file and returns a DataFrame with local time and all available frequency channels.
    
    Parameters:
    filepath (str): Path to the text file
    
    Returns:
    pd.DataFrame: DataFrame with datetime index and frequency columns
    """
    with open(filepath, 'r') as file:
        lines = file.readlines()

    # Find the header line that contains channel names
    header_line = None
    for line in lines:
        if re.search(r'FXE_A\d+', line):
            header_line = line
            break

    if not header_line:
        raise ValueError("Channel header line with FXE_A# not found.")

    # Extract channel names from header line
    headers = header_line.strip().split()
    channel_names = [h.split(':')[1] for h in headers if ':' in h]

    # Skip comment lines and blank lines
    data_lines = [line for line in lines if not line.strip().startswith('#') and line.strip()]

    records = []
    for line in data_lines:
        parts = line.split()
        if len(parts) >= (3 + len(channel_names)):
            date_str = parts[0]  # format: yymmdd
            time_str = parts[1]  # format: hhmmss.sss
            try:
                timestamp = pd.to_datetime(date_str + time_str, format='%y%m%d%H%M%S.%f')
                freqs = list(map(float, parts[3:3+len(channel_names)]))
                records.append([timestamp] + freqs)
            except Exception as e:
                print(f"Error parsing line: {line}\n{e}")

    columns = ['timestamp'] + channel_names
    df = pd.DataFrame(records, columns=columns)
    df.set_index('timestamp', inplace=True)

    return df

def plot_channel_8_analysis(df, channel_name='FXE_A8', f0=21.4e6, d_f=1, axs=None):
    """
    Creates a 4-panel plot:
    - Top-left: Last 12 hours of frequency data
    - Top-right: Histogram centered at f0 ± d_f over last 12 hours
    - Bottom-left: Last 1000 points of frequency data
    - Bottom-right: Allan deviation: 12-hour (red) and last 1000 points (blue)

    Parameters:
    df (pd.DataFrame): DataFrame with timestamp index and frequency columns
    channel_name (str): Name of the channel to analyze (default 'FXE_A8')
    f0 (float): Center frequency for zoom/histogram (default 21.4 MHz)
    d_f (float): Frequency span for histogram and Y-axis limits
    axs (list of Axes): Optional list of matplotlib Axes to reuse in persistent windows.
    """
    if channel_name not in df.columns:
        raise ValueError(f"Channel '{channel_name}' not found in DataFrame.")

    now = df.index.max()
    t12h = now - timedelta(hours=12)
    df_12h = df[df.index >= t12h]
    df_1000 = df.tail(1000)

    # Create or reuse figure
    if axs is None:
        fig, axs = plt.subplots(2, 2, figsize=(12, 6))
        axs = axs.flatten()

    # Clear each axis
    for ax in axs:
        ax.clear()

    # Top-left: Last 12h
    axs[0].plot(df_12h.index, df_12h[channel_name], '.', color='C0')
    axs[0].set_title(f"{channel_name} - Last 12 Hours")
    axs[0].set_ylim(f0 - d_f, f0 + d_f)
    axs[0].set_xlabel("Time")
    axs[0].set_ylabel("Frequency [Hz]")
    axs[0].grid(True)

    # Top-right: Histogram (±d_f)
    freqs_12h = df_12h[channel_name].dropna()
    freqs_filtered = freqs_12h[(freqs_12h >= f0 - d_f) & (freqs_12h <= f0 + d_f)]
    axs[1].hist(freqs_filtered, bins=100, range=(f0 - d_f, f0 + d_f),
                color='C0', orientation='horizontal')
    axs[1].set_title("Histogram (Last 12h)")
    axs[1].set_xlabel("Count")
    axs[1].set_ylabel("Frequency [Hz]")
    axs[1].set_ylim(f0 - d_f, f0 + d_f)
    axs[1].grid(True)

    # Bottom-left: Last 1000 points
    axs[2].plot(df_1000.index, df_1000[channel_name], '.', color='C0')
    axs[2].set_title("Last 1000 Points")
    axs[2].set_ylim(f0 - d_f, f0 + d_f)
    axs[2].set_xlabel("Time")
    axs[2].set_ylabel("Frequency [Hz]")
    axs[2].grid(True)

    # Bottom-right: Allan deviation
    rate = 1
    if len(freqs_12h) > 10:
        taus12, adev12, _, _ = allantools.oadev(freqs_12h.values, rate=rate, data_type='freq')
        axs[3].loglog(taus12, adev12, '-o', label='12h')
    y_1000 = df_1000[channel_name].dropna().values
    if len(y_1000) > 10:
        taus1000, adev1000, _, _ = allantools.oadev(y_1000, rate=rate, data_type='freq')
        axs[3].loglog(taus1000, adev1000, '-o', label='1000 pts')

    axs[3].set_title("Allan Deviation")
    axs[3].set_xlabel("Tau [s]")
    axs[3].set_ylabel("σ_y(τ)")
    axs[3].legend()
    axs[3].grid(True, which='both', ls='--')

    plt.tight_layout()
    plt.draw()