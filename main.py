import time
import os
from auxiliary import load_frequency_data, plot_channel_8_analysis

filename = "data/Freq_A_1_250521_1.txt"

while True:
    os.system('clear')  # or 'cls' for Windows
    print("Updating plot...")

    try:
        df = load_frequency_data(filename)
        plot_channel_8_analysis(df)
    except Exception as e:
        print(f"Error: {e}")

    time.sleep(5)  # update every 5 seconds

