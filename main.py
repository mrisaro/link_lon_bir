import time
import os
import matplotlib.pyplot as plt
from auxiliary import load_frequency_data, plot_channel_8_analysis

filename = "D:/FXX_App_Win_Ver_2.1.0_23-01-24/Logs/Freq_A_1_250522_1.txt"

plt.ion()  # Turn on interactive plotting

# Create the persistent figure once
fig, axs = plt.subplots(2, 2, figsize=(12, 6))
axs = axs.flatten()

while True:
    os.system('cls' if os.name == 'nt' else 'clear')
    print("Updating plot...")

    try:
        df = load_frequency_data(filename)
        plot_channel_8_analysis(df, axs=axs)  # Pass axes to update
    except Exception as e:
        print(f"Error: {e}")

    plt.pause(5)  # Pause 5 seconds before updating again
