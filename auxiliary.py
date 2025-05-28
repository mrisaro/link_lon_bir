import pandas as pd
import numpy as np
import os
import re
import allantools
import matplotlib.pyplot as plt
from datetime import datetime
from datetime import timedelta
import matplotlib.gridspec as gridspec

#------- Function find latest --------

def find_latest_file(folder, prefix="Freq_A_1_", suffix="_1.txt"):
    """
    Searches for a data file in the given folder that matches today's date pattern.

    Parameters:
    - folder (str): Path to the folder containing data files.
    - prefix (str): File name prefix before the date (default = 'Freq_A_1_').
    - suffix (str): File name suffix after the date (default = '_1.txt').

    Returns:
    - str: Full path to the matching file, or None if not found.
    """
    today = datetime.today().strftime('%y%m%d')
    expected_filename = f"{prefix}{today}{suffix}"
    full_path = os.path.join(folder, expected_filename)

    if os.path.isfile(full_path):
        return full_path
    else:
        print(f"[Warning] File not found for today's date: {expected_filename}")
        return None

#--------- Function load file ---------------

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

    # Clear all axes before plotting
    for ax in axs:
        ax.clear()

    # --- Plot 1: Last 12 hours ---
    axs[0].plot(df_12h.index, df_12h[channel_name], '.', color='C0')
    axs[0].set_title("Last 12 Hours")
    axs[0].set_ylim(f0 - d_f, f0 + d_f)
    axs[0].set_ylabel("Frequency [Hz]")
    axs[0].grid(True)

    # --- Plot 2: Histogram (last 12h ±d_f) ---
    freqs_12h = df_12h[channel_name].dropna()
    freqs_filtered = freqs_12h[(freqs_12h >= f0 - d_f) & (freqs_12h <= f0 + d_f)]
    axs[1].hist(freqs_filtered, bins=100, range=(f0 - d_f, f0 + d_f),
                orientation='horizontal', color='C0')
    axs[1].set_title("Histogram (Last 12h)")
    axs[1].set_ylim(f0 - d_f, f0 + d_f)
    axs[1].set_ylabel("Frequency [Hz]")
    axs[1].grid(True)

    # --- Box 1: Uptime ---
    total_points = len(df_12h)
    valid_points = freqs_12h.count()
    uptime_pct = 100 * valid_points / total_points if total_points > 0 else 0

    color = 'green' if uptime_pct >= 80 else 'gold' if uptime_pct >= 60 else 'red'
    axs[2].axis('off')
    axs[2].text(0.5, 0.6, "Uptime", fontsize=14, ha='center')
    axs[2].text(0.5, 0.3, f"{uptime_pct:.1f}%", fontsize=28, ha='center', color=color)

    # --- Plot 3: Last 1000 points ---
    axs[3].plot(df_1000.index, df_1000[channel_name], '.', color='C0')
    axs[3].set_title("Last 1000 Points")
    axs[3].set_ylim(f0 - d_f, f0 + d_f)
    axs[3].set_ylabel("Frequency [Hz]")
    axs[3].grid(True)

    # --- Plot 4: Allan deviation ---
    rate = 1
    if len(freqs_12h) > 10:
        taus12, adev12, _, _ = allantools.oadev(freqs_12h.values, rate=rate, data_type='freq')
        axs[4].loglog(taus12, adev12, 'r.-', label='12h')
    y_1000 = df_1000[channel_name].dropna().values
    if len(y_1000) > 10:
        taus1000, adev1000, _, _ = allantools.oadev(y_1000, rate=rate, data_type='freq')
        axs[4].loglog(taus1000, adev1000, 'b.-', label='1000 pts')
    axs[4].set_title("Allan Deviation")
    axs[4].set_xlabel("Tau [s]")
    axs[4].set_ylabel("σ_y(τ)")
    axs[4].legend()
    axs[4].grid(True, which='both', ls='--')

    # --- Box 2: Glitch Rate ---
    glitch_thresh = 2  # Hz
    glitches = freqs_12h[np.abs(freqs_12h - f0) > glitch_thresh]
    glitch_rate = 100 * len(glitches) / valid_points if valid_points > 0 else 0

    axs[5].axis('off')
    axs[5].text(0.5, 0.6, "Glitch Rate", fontsize=14, ha='center')
    axs[5].text(0.5, 0.3, f"{glitch_rate:.2f}%", fontsize=24, ha='center', color='black')

    plt.tight_layout()
    plt.draw()