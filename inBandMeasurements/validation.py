import sys
import os
import time
import pdb
from multiprocessing import Process, Event
import subprocess
import pandas as pd
from uprof.edittimechart import runner
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np
from sklearn.model_selection import TimeSeriesSplit

# This will be used to setUp PowerPack
settingUpDaqPath = os.path.abspath("../settingUpDaq")
if os.path.exists(settingUpDaqPath) and settingUpDaqPath not in sys.path:
    sys.path.append(settingUpDaqPath)
from powerMeasurer import PowerPack

class PartValidation:
    '''
    This class is meant to validate different parts within
    the PowerPack Node
    '''

    def __init__(self, part:str, sampleRate:int):
        '''
        This will initialize all the parts, and profiler of
        interest
        '''
        self.part = part
        self.profiler = None
        self.sampleRate = sampleRate          
        self.PowerPack = PowerPack(numberOfSamplesToGather=2000, rateOfSamples=sampleRate, ohms=0.003)
    
    def setUp(self):
        if self.part == "gpu":

            parts = {
                    'gpu': [
                    [],
                    [],
                    ["cDAQ2Mod2/ai0","cDAQ2Mod2/ai1","cDAQ2Mod2/ai2", "cDAQ2Mod2/ai3"]
                ]
            }

        elif self.part == "cpu":

            parts = {
                    'cpu': [
                    [],
                    [],
                    ["cDAQ2Mod2/ai4","cDAQ2Mod2/ai5","cDAQ2Mod2/ai6", "cDAQ2Mod2/ai7"]
                ]
            }
        else:
            raise ValueError("Invalid input! for initialzing class")

        self.PowerPack.initializePart(parts)
    
    def _setUpProfiler(self):
        
        if self.part == "cpu":
            self.profiler = Process(target=lambda: subprocess.run(['./profiler.sh']))
        
        elif self.part == "gpu":
            self.profiler = Process(target=lambda: subprocess.run(['./GPUprofiler.sh']))
        
        else:
            raise ValueError("Invalid input! for initializing the class")
        
        
    
    def _testRunner(self):
        if self.part == "cpu":

            self.runner = Process(target=lambda: subprocess.run(['python', './communicationTest.py']))

        elif self.part == "gpu":
            self.runner = Process(target=lambda: subprocess.run(['python', './GPUCommunication.py']))
        
        
        if len(self.part) > 0:
            os.chdir('./benchmarking/')
            self.runner.start()
            os.chdir('../')

        else:
            raise ValueError("Bad initializing of class")

    def _profileCleaner(self):

        
        if self.part == "cpu":
            subprocess.run(["./uprof/csv-line-remover.sh"])

            # This will read in the desired time chart reader
            df = pd.read_csv('./uprof/timechart.csv')

            # Dropping the Record Id label
            df.drop('RecordId', axis=1, inplace=True)

            df.rename(columns={'socket0-package-power': 'Power'}, inplace=True)

            # This will turn all the time stamps into date time objects
            df['Timestamp'] = df['Timestamp'].apply(lambda x: datetime.strptime(x, '%H:%M:%S:%f'))

            df['time_in_seconds'] = (df['Timestamp'] - df['Timestamp'].min()).dt.total_seconds()

        elif self.part == "gpu":

            df = pd.read_csv('gpuPow.csv', header=None, names=["Timestamp", "Power"])
            df['Timestamp'] = pd.to_datetime(df['Timestamp'], format='%Y-%m-%d %H:%M:%S')
            df['Power'] = df['Power'].str.replace(' W', '').astype(float)


            df['time_in_seconds'] = (df['Timestamp'] - df['Timestamp'].min()).dt.total_seconds()


        return df

    
    def runPart(self, profilerBool:bool=False, power_packBool:bool=False, bothBool:bool=False):
        '''
        Specify the type of run
        '''

        # Choosing what to run
        if bothBool:
            self._setUpProfiler()
            self.profiler.start()
            self.PowerPack.start()


            self._testRunner()
            self.runner.join()
            

            if (self.part == "cpu"):
                # Stop the profiler
                self.profiler.join()
            else:
                self.profiler.terminate()
                self.profiler.join()
                self.profiler.kill()
                print(self.profiler.is_alive())

            # End power pack
            self.PowerPack.stop()


            # Call the graphs on both
            self._graphs(bothBool=True)

        
        elif profilerBool:
            self._setUpProfiler()
            self.profiler.start()
            
            self._testRunner()
            self.runner.join()

            if (self.part == "cpu"):
                # Stop the profiler
                self.profiler.join()
            else:
                self.profiler.terminate()
                self.profiler.join()


            # Call the graphs on profiler
            self._graphs(profilerBool=True)


        elif power_packBool:

            self.PowerPack.start()
            self._testRunner()
            self.runner.join()
            self.PowerPack.stop()


             # Call the graphs on power pack
            self._graphs(power_packBool=True)

        else:
            raise ValueError("Internal Error")
        
    
    
    def _powerPackAnalyzer(self):
        
        self.PowerPack.makeCSVs()

        if self.part == "cpu":
            powerPackDf = pd.read_csv('./csv/cpuMeasurements.csv')
        elif self.part == "gpu":
            powerPackDf = pd.read_csv('./csv/gpuMeasurements.csv')
        else:
            raise ValueError("Initializing error")


        # setting up a dataframe, and including a way too sum up all the wires
        powerPackDf['voltage sum'] = powerPackDf.sum(axis=1)


        # This is for taking the time from the front of the array
        times = np.arange(0, powerPackDf.shape[0]) / self.sampleRate
        powerPackDf['Times'] = times


        # Parameters, the loss is (window size + 1)
        window_size = 250
        voltage_sum = powerPackDf['voltage sum'].values
        times = powerPackDf['Times'].values

        # Create sliding windows using the strided trick
        voltage_windows = np.lib.stride_tricks.sliding_window_view(voltage_sum, window_shape=window_size)
        time_windows = np.lib.stride_tricks.sliding_window_view(times, window_shape=window_size)

        # Compute medians and variances for all windows at once
        voltage_medians = np.median(voltage_windows, axis=1)

        # Use the last time in each window for timing
        # reference_times = time_windows[:, -1]
        reference_times = np.median(time_windows, axis=1)

        # Create the DataFrame with the computed values
        median_window = pd.DataFrame({
            'times': reference_times,
            'voltage_median': voltage_medians
        })

        return median_window


    
    
    def _graphs(self, profilerBool:bool=False, power_packBool:bool=False, bothBool:bool=False):
        
        if bothBool:
        
            df = self._profileCleaner()
            plt.plot(df['time_in_seconds'], df['Power'], label="Profiler", color ="blue")

            # plotting the power pack data
            dfPowerPack = self._powerPackAnalyzer()
            plt.plot(dfPowerPack['times'], dfPowerPack['voltage_median'], label='Window median', color = "red")

        elif profilerBool:
            df = self._profileCleaner()
            plt.plot(df['time_in_seconds'], df['Power'], label="Profiler", color ="blue")
        elif power_packBool:
            # plotting the power pack data
            dfPowerPack = self._powerPackAnalyzer()
            plt.plot(dfPowerPack['times'], dfPowerPack['voltage_median'], label='Window median', color = "red")
        else:
            raise ValueError("Internal Error")
            
        # Display the plot
        plt.xlabel('Time (seconds)')
        plt.ylabel('Power Consumption (Watts)')
        plt.title(f'Power Consumption of {str(self.part).upper()} Over Time')
        plt.grid(True)
        plt.savefig(f'./graphs/{str(self.part)}.png')
        plt.show()

        
        
