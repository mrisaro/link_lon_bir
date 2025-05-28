import time
import os
import matplotlib.pyplot as plt
from auxiliary import load_frequency_data, plot_channel_8_analysis, find_latest_file

# --- Config ---
data_folder = "D:/FXX_App_Win_Ver_2.1.0_23-01-24/Logs/"
channel_name = "FXE_A8"
f0 = 21.4e6
d_f = 1
refresh_interval = 10  # seconds

# --- Setup interactive plot ---
plt.ion()
fig = plt.figure(figsize=(14, 7))
gs = fig.add_gridspec(2, 3, width_ratios=[4, 4, 2])  # 40%, 40%, 20%
axs = [fig.add_subplot(gs[i, j]) for i in range(2) for j in range(3)]

# --- Main update loop ---
while True:
    os.system('cls' if os.name == 'nt' else 'clear')
    print("[INFO] Updating plot...")

    filename = find_latest_file(data_folder)

    if filename:
        try:
            df = load_frequency_data(filename)
            plot_channel_8_analysis(df, channel_name=channel_name, f0=f0, d_f=d_f, axs=axs)
        except Exception as e:
            print(f"[ERROR] Failed to plot: {e}")
    else:
        print("[WARNING] No file found for today.")

    plt.pause(refresh_interval)