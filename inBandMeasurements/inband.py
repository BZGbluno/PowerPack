import sys
import os
import time
import pdb
from multiprocessing import Process
import subprocess
import pandas as pd
from uprof.edittimechart import runner
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np

# adding the path to the global path 
settingUpDaqPath = os.path.abspath("../settingUpDaq")
if os.path.exists(settingUpDaqPath) and settingUpDaqPath not in sys.path:
    sys.path.append(settingUpDaqPath)
from powerMeasurer import PowerPack
from sklearn.model_selection import TimeSeriesSplit


def runCommunication():
    os.chdir('./benchmarking/')
    subprocess.run(['python', 'communicationTest.py'])


# Sampling rate
samplingRate = 50000
Power = PowerPack(numberOfSamplesToGather=2000, rateOfSamples=samplingRate, ohms=0.003)


# We are only interested in the CPU currently
cpu = [
        [],
        [],
        ["cDAQ2Mod2/ai4","cDAQ2Mod2/ai5","cDAQ2Mod2/ai6", "cDAQ2Mod2/ai7"]
    ]

# Initialize the part
Power.initializePart("cpu", cpu)


# Start Power Pack
Power.start()

runCommunication()


# Stop measurement task
Power.stop()

# change directory back
os.chdir('../')

# make the CSV
Power.makeCSVs()


# setting up a dataframe, and including a way too sum up all the wires
powerPackDf = pd.read_csv('./csv/cpuMeasurements.csv')
powerPackDf['voltage sum'] = powerPackDf.sum(axis=1)


# This is for taking the time from the front of the array
times = np.arange(0, powerPackDf.shape[0]) / samplingRate
powerPackDf['Times'] = times



# setting up the median window for times, voltage median, and voltage variance
median_window = pd.DataFrame(columns=['times', 'voltage_median', 'voltage_var'])

# Parameters, the loss is (window size + 1)
window_size = 100
voltage_sum = powerPackDf['voltage sum'].values
times = powerPackDf['Times'].values

# Create sliding windows using the strided trick
voltage_windows = np.lib.stride_tricks.sliding_window_view(voltage_sum, window_shape=window_size)
time_windows = np.lib.stride_tricks.sliding_window_view(times, window_shape=window_size)

# Compute medians and variances for all windows at once
voltage_medians = np.median(voltage_windows, axis=1)

# Use the last time in each window for timing
reference_times = time_windows[:, -1]

# Create the DataFrame with the computed values
median_window = pd.DataFrame({
    'times': reference_times,
    'voltage_median': voltage_medians
})


# plotting the data
plt.rcParams["figure.figsize"] = (16,6)
plt.rcParams['figure.dpi'] = 200
plt.figure()

# plotting the power pack data
plt.plot(median_window['times'], median_window['voltage_median'], label='Window median', color = "red")



# Display the plot
plt.xlabel('Time (seconds)')
plt.ylabel('Power Consumption (Watts)')
plt.title('Power Consumption of CPU Over Time')
plt.legend()
plt.grid(True)
plt.savefig('./graphs/cpu.png')
plt.show()
