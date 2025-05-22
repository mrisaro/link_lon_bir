# Optical Fiber Link Monitor

This project is intended to generate a live report on the status of actively running optical fiber links. The initial focus is on the **London–Birmingham** and **London–Paris** links, but the idea is to extend this structure to all monitored links over time.

The aim is to collect and process frequency data from **K+K frequency counters** to lively characterize the optical link's performance. The tool will serve as a permanent monitor to help determine whether:
- The link is operating properly, or
- It is necessary to make an intervention in the lab.

### 🔍 Current Focus

- Active development and testing is focused on the **London–Birmingham** link.
- The data used is stored in `.txt` format from K+K counters (e.g., `Freq_A_1_yymmdd_1.txt`), located in the `data/` folder.

---

## 📁 Repository Structure

```bash
.
├── auxiliary.py        # Helper functions for loading and plotting frequency data
├── main.py             # Main script for running live or static analysis
├── data/               # Folder containing raw .txt frequency log files
└── README.md           # This file
```

## ✅ Features Implemented

- **`load_frequency_data(filepath)`**  
  Reads and parses a `.txt` file from the frequency counter, returning a DataFrame with timestamps and frequency data of the channels in each column.

- **`plot_channel_8_analysis(df, channel_name='FXE_A8', f0=21.4e6, d_f=1)`**  
  Plots a 4-panel diagnostic plot for Channel 8:
  - Top-left: Last 12 hours of frequency data
  - Top-right: Histogram (±d_f around f0)
  - Bottom-left: Last 1000 points of frequency data
  - Bottom-right: Allan deviation (12h in red, 1000 pts in blue)

- **Live console plotting loop (`main.py`)**  
  Runs in a terminal, refreshing the plot every 5 or 10 seconds using the latest available data.

---

## 🚀 How to Use

1. **Place the raw data file** in the `data/` folder. Example filename:  Freq_A_1_250521_1.txt

2. **Import and use the analysis functions** from the Python console or another script:
```python
from auxiliary import load_frequency_data, plot_channel_8_analysis

df = load_frequency_data("data/Freq_A_1_250521_1.txt")
plot_channel_8_analysis(df)

3. **To enable live monitoring** run the main script: python main.py
