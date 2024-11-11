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

settingUpDaqPath = os.path.abspath("../settingUpDaq")
if os.path.exists(settingUpDaqPath) and settingUpDaqPath not in sys.path:
    sys.path.append(settingUpDaqPath)
from powerMeasurer import PowerPack
from sklearn.model_selection import TimeSeriesSplit


type = sys.argv[1]
test = sys.argv[2]

samplingRate = 50000
Power = PowerPack(numberOfSamplesToGather=2000, rateOfSamples=samplingRate, ohms=0.003)

plt.rcParams["figure.figsize"] = (16,6)
plt.rcParams['figure.dpi'] = 200
plt.figure()



def runProfiler():
    if (type == 'cpu'): 
        subprocess.run('./profiler.sh')
    else: #if (type == 'gpu')
        subprocess.run('') #INSERT THE name of the script to run the gpu program



def PowerPackSetUp(): 
    if (type == 'cpu'): 
        cpu = [
            [],
            [],
            ["cDAQ2Mod2/ai4","cDAQ2Mod2/ai5","cDAQ2Mod2/ai6", "cDAQ2Mod2/ai7"]
            ]

        # Initialize the part
        Power.initializePart("cpu", cpu)
    else: #CHANGE NAMES OF THE ARRAY VALUES
        gpu = [
            [],
            [],
            ["cDAQ2Mod2/ai0","cDAQ2Mod2/ai1","cDAQ2Mod2/ai2", "cDAQ2Mod2/ai3"]
            ]
        Power.initializePart("gpu", gpu)
    
    Power.start()



def runCommunication():
    os.chdir('./benchmarking/')
    if (type == 'cpu'): #change value at communicationTest.py to be a variable that can be edited in terminal
        subprocess.run(['python', 'communicationTest.py'])
    else: 
        subprocess.run(['python', 'INSERT GPU TEST.py']) #insert gpu test



def afterPowerPack(): 
    if (type == 'cpu'): 
        powerPackDf = pd.read_csv('./csv/cpuMeasurements.csv')
    else: #CREATE THIS GPU CSV
        powerPackDf = pd.read_csv('./csv/gpuMeasurements.csv')

    powerPackDf['voltage sum'] = powerPackDf.sum(axis=1)

    # This is for taking the time from the front of the array
    times = np.arange(0, powerPackDf.shape[0]) / samplingRate
    powerPackDf['Times'] = times

    #calls the next method
    medianWindow(powerPackDf)


def medianWindow(powerPackDf): 
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

    plt.plot(median_window['times'], median_window['voltage_median'], label='Window median', color = "red")



def afterProfiler(): 
    #cleaning the files
    if (type == 'cpu'): 
        df = runner()
    else: 
        #INSERT DATAFRAME FOR GPU test, change line below so df = 'INSERT GPU TEST'()
        df = runner()

    print(os.getcwd())

    plt.plot(df['time_in_seconds'], df['socket0-package-power'], label="Profiler", color ="blue")





if (test == 'both'): 
    profiler = Process(target=runProfiler)
    PowerPackSetUp()
    profiler.start()

    runCommunication()
    os.chdir('../')

    # terminate the profiler and join the child process for synchronization
    profiler.terminate()
    profiler.join()

    Power.stop()
    Power.makeCSVs()
    afterPowerPack()
    afterProfiler()

elif (test == 'PowerPack'): 
    PowerPackSetUp()

    runCommunication()
    os.chdir('../')

    Power.stop()
    Power.makeCSVs()
    afterPowerPack()

elif (test == 'profiler'): 
    profiler = Process(target=runProfiler)
    profiler.start()

    runCommunication()
    os.chdir('../')

    # terminate the profiler and join the child process for synchronization
    profiler.terminate()
    profiler.join()

    time.sleep(10)

    afterProfiler()


# Display the plot
plt.xlabel('Time (seconds)')
plt.ylabel('Power Consumption (Watts)')
plt.ylim(0,100)
plt.legend()
plt.grid(True)
if (type == 'cpu'): 
    plt.title('Power Consumption of CPU Over Time')
    plt.savefig('./graphs/both.png')
else: #if (type == 'gpu')
    plt.title('Power Consumption of GPU Over Time')
    plt.savefig('./graphs/gpu.png')
plt.show()