import nidaqmx
from nidaqmx.constants import TerminalConfiguration
from nidaqmx.stream_readers import AnalogMultiChannelReader
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
import threading
import os
from datetime import datetime


class Measurements:
    '''

    This class handles the power measurement of a mentioned part. It will store all power
    reading data into an matrix. That matrix can be made into either a plot it into a graph
    or create a CSV for it

    Important: The linesNamesMatrix must be in a matrix with 3 rows even if channel names don't
               exist for some.
        
        Convention:
            [
                [3.3volts],\n
                [5volts],\n
                [12volts],          
            ]

        Example: [
                    [3v_channel_pair_name1, 3v_channel_pair_name2, ...],\n
                    [5v_channel_pair_name1, 5v_channel_pair_name2, ...],\n
                    [12v_channel_pair_name1, 12v_channel_pair_name2, ...]
                ]
    
    Methods:
        __init__(self, numberOfSamplesToGather: int, rateOfSamples: int, ohms, linesNamesMatrix, name:str):
            -Initializes a new instance

        getName(self):
            -returns the name of the part
        
        runTask(self, stop_event):
            -creates and runs the task while saving all the data. Task ends once stop event is triggered

        makeCSV(self):
            -This will turn the data attribute into a CSV and save it in a CSV directory

        plot(self, times):
            -This will plot the data and save it in a Graph directory
        
        lengths(self):
            -This will retrieve the length of all the samples combined

    '''

    def __init__(self, numberOfSamplesToGather: int, rateOfSamples: int, ohms, linesNamesMatrix, name:str):
        '''
        This will initialize all the data to make a task

        Args:
            numberOfSamples (int): Number of tasks read before callback function is called

            rateOfSamples (int): Samples per second that the NI 9205 modules are reading

            ohms (int): The resistance amount

            linesNamesMatrix
            name (str)  
        '''
        
        self.numOfSamples = numberOfSamplesToGather
        self.rateOfSamples = rateOfSamples
        self.ohms = ohms
        self.name = name
        self.totalLines = 0
        self.data = {}
        self.times = []



        self.parts = linesNamesMatrix
        self.channelOrder = []
        self.channelVoltageMap = {}
        self.channelSamples = {}
        self.partCount = 0

        
        self._setLineNames(linesNamesMatrix)

    
    def _setLineNames(self, linesNamesMatrix):
        '''
        This is a private method that will create a sample array for the available channels
        '''
        totalLine = 0

        for part in linesNamesMatrix.keys():

            for index, row in enumerate(linesNamesMatrix[part]):

                for channel in row:

                    voltage = 0
                    if index == 0:
                        voltage = 3.3
                    
                    
                    elif index == 1:
                        voltage = 5

                    elif index == 2:
                        voltage = 12
                    
                    
                    self.channelVoltageMap[channel] = [voltage, part]
                    self.channelSamples[channel] = []
                    totalLine += 1
            self.partCount += 1

        self.totalLines += totalLine

    

    def getChannelVoltMap(self):
        return self.channelVoltageMap
    
    def getTotalLines(self):
        return self.totalLines
    
    def getChannelSamples(self):
        return self.channelSamples

    def getName(self):
        '''
        Returns the name of the part that we are measuring
        '''
        return self.name
        

    def runTask(self, stop_event):
        '''
        Creates and runs the task while saving all the data. Task ends once stop event is triggered
        '''
        try:

            task = nidaqmx.Task(f"Measure {self.name} consumption")


            for key in self.channelVoltageMap.keys():
                # add in order here
                
                self.channelOrder.append(key)
                task.ai_channels.add_ai_voltage_chan(f"{key}", terminal_config=TerminalConfiguration.DIFF)

            # Setting up the sampling rates
            task.timing.cfg_samp_clk_timing(
                rate=self.rateOfSamples,
                sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS,
                samps_per_chan=self.numOfSamples
            )
            reader = AnalogMultiChannelReader(task.in_stream)


            # Define a callback function, it is here because task will go out of scope if placed outside
            # the number of samples is used for a callback function to read out the samples
            def callback(task_handle, every_n_samples_event_type, number_of_samples, callback_data):
                try:
                    # checks if the task is an instance of a task
                    if isinstance(task, nidaqmx.Task) == False:
                        print("failed")
                    data = np.zeros((self.totalLines,number_of_samples), dtype=np.float64)
                    
                    # Create a stream reader
                    reader.read_many_sample(data, number_of_samples)


                        
                    for row in range(0, self.totalLines):

                        data[row] = np.clip(data[row], -1e10, 1e10)  # Prevent overflow
                        voltage = int((self.channelVoltageMap[self.channelOrder[row]])[0])
                        # Append the processed data
                        self.channelSamples[self.channelOrder[row]] = np.concatenate((self.channelSamples[self.channelOrder[row]] , abs((data[row]/self.ohms)*voltage)))
                        # self.channelSamples[self.channelOrder[row]] = np.concatenate((self.channelSamples[self.channelOrder[row]] , abs((data[row]))))


                    
                    return 0
                except nidaqmx.errors.DaqError as e:
                    print(f"NI-DAQ error in callback: {e}")
                    return -1
                except Exception as ex:
                    print(f"Exception in callback function: {ex}")
                    return -1
            
            # Register the callback function
            task.register_every_n_samples_acquired_into_buffer_event(self.numOfSamples, callback)

            # Start the task
            task.start()

            # Keep task running until stop_event is set
            while not stop_event.is_set():
                    time.sleep(0.1)
        

        except nidaqmx.errors.DaqError as e:
            print(f"NI-DAQ error occurred: {e}")
        except Exception as ex:
            print(f"Exception occurred in NI-DAQ thread: {ex}")
        finally:
            # Clean up the task
            if 'task' in locals() and task is not None:
                task.stop()
                task.close()

                # # self._fixTime()
                # print(self.channelSamples)
                self._fillData()


    def _fixTime(self):
        initialTime = self.times[0]
        for index, x in enumerate(self.times):
            self.times[index] = self.times[index] - initialTime

    
        


    def _fillData(self):
        '''
        This will make a matrix of data containing with the rows being the different channels
        and the columns are the different samples gathered with the first 2 columns being the channel
        name and volt readings respectively
        '''

        mixedName = ""
        # making graph for individual parts
        for part in self.parts.keys():
            mixedName = str(part) + mixedName
            df = pd.DataFrame()

            
            # Find the smallest sample within the channels
            smallestArr = []
            for channels in self.channelOrder:
                
                if part == self.channelVoltageMap[channels][1]:
                    smallestArr.append(len(self.channelSamples[channels]))

            smallest = min(smallestArr)

            for channels in self.channelOrder:
                
                if part == self.channelVoltageMap[channels][1]:

                    voltage = self.channelVoltageMap[channels][0]
                    df[f"{channels} with {voltage} Volts"] = self.channelSamples[channels][0:smallest]
            

            self.data[part] = df
        
        self.length = len(self.data[part])


        if (self.partCount > 1):
            
            # dataset for combined parts
            df1 = pd.DataFrame()
            for channels in self.channelOrder:

                voltage = self.channelVoltageMap[channels][0]
                df1[f"{self.channelVoltageMap[channels][1]} using {channels} with {voltage} Volts"] = pd.Series(self.channelSamples[channels])
            
            self.data[mixedName] = df1



    
    def makeCSV(self):
        '''
        This will turn the data matrix into a CSV and save it to
        a directory named CSV
        '''

        if not os.path.exists("./csv"):
            os.makedirs("./csv")
        for datasets in self.data.keys():

            self.data[datasets] = self.data[datasets].dropna()

            filepath = f'./csv/{datasets}Measurements.csv'
            self.data[datasets].to_csv(filepath, index=False)





    def plot(self, times, partToPlot, powerCap, verticalAsymtotes=None, pattern=None):
        
        '''
        This will turn the data matrix into a graph and save it 
        a directoy named graph.
        '''
        self.data[f'{partToPlot}']['voltage sum'] = self.data[f'{partToPlot}'].sum(axis=1)

        voltageAmounts = []

        for volt in self.data[f'{partToPlot}']['voltage sum']:
            voltageAmounts.append(volt)


        self._tempPlot(times, partToPlot, powerCap, voltageAmounts, verticalAsymtotes, pattern)   

            


    
    def _tempPlot(self, time, name, powerCap, voltageAmount, verticalAsymtotes=None, pattern=None):
        '''
        This will plot the different lines which are arrays as the y-axis and
        the x-axis is the time array. This is a private method to help with
        plotting. It will also add vertical Asymtote to the graph if they exist
        '''

        plt.rcParams["figure.figsize"] = (16,6)
        plt.rcParams['figure.dpi'] = 300
        
        plt.figure()

        if verticalAsymtotes:
            count = 0

            for asymptote in verticalAsymtotes:

                calculateColor = count % pattern
                count+=1

                # rounded = str(round(asymptote[0]))
                # plt.axvline(x=float(asymptote), color='b', label=f'Start time, ')

                rounded_asymptote = round(asymptote, 4)  # Round to 2 decimal places

                if calculateColor == 1:
                    value = 'b'
                else: 
                    value = 'g'
                plt.axvline(x=float(asymptote), color=value, label=f'Start time: {rounded_asymptote:.4f}')
 

        df = pd.DataFrame({
            'voltage': voltageAmount,
            'times': time
        })

        # setting up the median window for times, voltage median, and voltage variance
        median_window = pd.DataFrame(columns=['times', 'voltage_median', 'voltage_var'])

        # Parameters, the loss is (window size + 1)
        window_size = 100
        voltage_sum = df['voltage'].values
        times = df['times'].values


        # Create sliding windows using the strided trick
        voltage_windows = np.lib.stride_tricks.sliding_window_view(voltage_sum, window_shape=window_size)
        time_windows = np.lib.stride_tricks.sliding_window_view(times, window_shape=window_size)

        
        # Compute medians for all windows at once
        voltage_medians = np.median(voltage_windows, axis=1)

        # Use the last time in each window for timing
        reference_times = time_windows[:, -1]

        # Create the DataFrame with the computed values
        median_window = pd.DataFrame({
            'times': reference_times,
            'voltage_median': voltage_medians
        })
        
        plt.plot(median_window['times'], median_window['voltage_median'], label=f'PowerPack Measurements: {name}', color = "red")

        plt.xlabel('Time (seconds)')
        plt.ylabel('Watts')
        plt.title(f'{name.upper()} Power Consumption Graph (Power Cap = {powerCap}W)')
        plt.legend()
        plt.grid(True)
        ax = plt.gca()
        ax.xaxis.set_major_locator(ticker.MultipleLocator(base=2)) #how much x-axis is incremented by

        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d %H:%M:%S")

        # if folder does not exist, create it
        graphs_folder = "./graphs"
        if not os.path.exists(graphs_folder):
            os.mkdir(graphs_folder)

        # Add plot to folder
        plt.savefig(f'./graphs/{name}_with_{powerCap}_{date_str}.png')
        plt.close()


    def lengths(self):
        '''
        This will return the amount of samples gathered by a channel
        '''
        return self.length
    




    

        


