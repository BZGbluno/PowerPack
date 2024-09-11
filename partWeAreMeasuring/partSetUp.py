from partWeAreMeasuring.constants import Voltages
import nidaqmx
from nidaqmx.constants import TerminalConfiguration
from nidaqmx.stream_readers import AnalogMultiChannelReader
import time
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd


class Measurements:
    '''

    This class handles the power measurement of a mentioned part. It will store all power
    reading data into an matrix. That matrix can be made into either a plot it into a graph
    or create a CSV for it

    Important: The linesNamesMatrix must be in a matrix with 3 rows even if channel names don't
               exist for some.
        
        Convention:
            [
                [3volts],\n
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
        self.threeVoltsSamples = {}
        self.fiveVoltsSamples = {}
        self.twelveVoltsSamples = {}
        self.totalLines = 0
        self.data = []
        self.times = []

        # 3.3 Volt Lines is row 0
        self._setLineNames(linesNamesMatrix, 0)

        # 5 Volt Lines is row 1
        self._setLineNames(linesNamesMatrix, 1)

        # 12 Volt Lines is row 2
        self._setLineNames(linesNamesMatrix, 2)

    
    def _setLineNames(self, linesNamesMatrix, row):
        '''
        This is a private method that will create a sample array for the available channels
        '''
        totalLine = 0
        for names in linesNamesMatrix[row]:
            channelName = f"{names}"
            samples = []
            if row == 0:
                self.threeVoltsSamples[channelName] = samples
            elif row == 1:
                self.fiveVoltsSamples[channelName] = samples
            else:
                self.twelveVoltsSamples[channelName] = samples


            totalLine += 1
        self.totalLines += totalLine
    

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

            # Channels added for 3.3V measurements
            for key in self.threeVoltsSamples.keys():
                task.ai_channels.add_ai_voltage_chan(f"{key}", terminal_config=TerminalConfiguration.DIFF)

            # Channels added for 5V measurements
            for key in self.fiveVoltsSamples.keys():
                task.ai_channels.add_ai_voltage_chan(f"{key}", terminal_config=TerminalConfiguration.DIFF)

            # Channels added for 12V measurements
            for key in self.twelveVoltsSamples.keys():
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

                    for x in range(number_of_samples):

                        
                        
                        # 3.3 volt
                        index = 0
                        for key in self.threeVoltsSamples.keys():
                            #print(data)
                            self.threeVoltsSamples[key].append(abs((Voltages.THREEVOLTS.value * (data[index][x])/self.ohms)))
                            #self.threeVoltsSamples[key].append(abs((data[index][x])))
                            #print(data[index][x])
                            index += 1
                            #print(self.threeVoltsSamples)

                        # 5 volts
                        index = 0
                        for key in self.fiveVoltsSamples.keys():
                            self.fiveVoltsSamples[key].append(abs((Voltages.FIVEVOLTS.value * (data[index][x])/self.ohms)))
                            #self.fiveVoltsSamples[key].append(abs((data[index][x])))
                            index += 1
                        
                        # 12 volts
                        index = 0
                        for key in self.twelveVoltsSamples.keys():
                            self.twelveVoltsSamples[key].append(abs((Voltages.TWELVEVOLTS.value * (data[index][x])/self.ohms)))
                            #self.twelveVoltsSamples[key].append(abs((data[index][x])))
                            index += 1
                        


                    # Process the data
                    # print(f"Data shape: {data.shape}")
                    # print(f"Data: {data}")
                    
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
                task.close()

                # self._fixTime()
                self._fillData()

    def _fixTime(self):
        initialTime = self.times[0]
        for index, x in enumerate(self.times):
            self.times[index] = self.times[index] - initialTime



        print(self.times)
    
            
        


    def _fillData(self):
        '''
        This will make a matrix of data containing with the rows being the different channels
        and the columns are the different samples gathered with the first 2 columns being the channel
        name and volt readings respectively
        '''
        df = pd.DataFrame()

        # this will get the column names
        for key in self.threeVoltsSamples:
            df[f"{key} with 3.3 Volts"] = pd.Series(self.threeVoltsSamples[key])


        for key in self.fiveVoltsSamples:
            df[f"{key} with 5 Volts"] = pd.Series(self.fiveVoltsSamples[key])


        for key in self.twelveVoltsSamples:
            df[f"{key} with 12 Volts"] = pd.Series(self.twelveVoltsSamples[key])

        self.data = df

    
    def makeCSV(self):
        '''
        This will turn the data matrix into a CSV and save it to
        a directory named CSV
        '''

        filepath = f'./csv/{self.name}Measurements.csv'
        self.data.to_csv(filepath, index=False)


    def plot(self, times, verticalAsymtotes=None):
        '''
        This will turn the data matrix into a graph and save it 
        a directoy named graph.
        '''

        dataWithNoChannelInfo = []
        voltageAmounts = []

        self.data['voltage sum'] = self.data.sum(axis=1)
        
        
        for volt in self.data["voltage sum"]:
            voltageAmounts.append(volt)


        print(len(times))
        print(len(voltageAmounts))

        self._tempPlot(times, self.name, voltageAmounts, verticalAsymtotes)   

        

        #self._plotGraphs(times, dataWithNoChannelInfo, self.name, voltageAmounts, verticalAsymtotes)


    
    def _tempPlot(self, time, name, voltageAmount, verticalAsymtotes=None):
        '''
        This will plot the different lines which are arrays as the y-axis and
        the x-axis is the time array. This is a private method to help with
        plotting. It will also add vertical Asymtote to the graph if they exist
        '''

        plt.rcParams["figure.figsize"] = (16,6)
        plt.rcParams['figure.dpi'] = 200
        
        plt.figure()

        if verticalAsymtotes:
            for asymtote in verticalAsymtotes:
                plt.axvline(x=float(asymtote), color='r', linestyle='--', label=f'{verticalAsymtotes[asymtote]}')

        # for index, line in enumerate(lines):
        #     #plt.plot(time, line, label=f'{voltageAmount[index]} line', lw=0.5)
        #     plt.scatter(time, line, label=f'{voltageAmount[index]} line', s=2)#, lw=2)

        #plt.plot(time, voltageAmount, lw=0.5, label="cpu")
        
        plt.scatter(time, voltageAmount, label='line', s=2)

        plt.xlabel('Time in sec')
        plt.ylabel('Watts')
        plt.title(f'{name} Power Consumption Graph')
        plt.legend()
        plt.grid(True)
        ax = plt.gca()
        ax.xaxis.set_major_locator(ticker.MultipleLocator(base=0.5))
        plt.savefig(f'./graphs/{name}.svg')
        plt.savefig(f'./graphs/{name}.png')
        plt.show


    def _plotGraphs(self, time, lines, name, voltageAmount, verticalAsymtotes=None):
        '''
        This will plot the different lines which are arrays as the y-axis and
        the x-axis is the time array. This is a private method to help with
        plotting. It will also add vertical Asymtote to the graph if they exist
        '''

        plt.rcParams["figure.figsize"] = (16,6)
        plt.rcParams['figure.dpi'] = 200
        
        plt.figure()

        if verticalAsymtotes:
            for asymtote in verticalAsymtotes:
                plt.axvline(x=float(asymtote), color='r', linestyle='--', label=f'{verticalAsymtotes[asymtote]}')

        for index, line in enumerate(lines):
            #plt.plot(time, line, label=f'{voltageAmount[index]} line', lw=0.5)
            plt.scatter(time, line, label=f'{voltageAmount[index]} line', s=2)#, lw=2)

        plt.plot

        plt.xlabel('Time in sec')
        plt.ylabel('Watts')
        plt.title(f'{name} Power Consumption Graph')
        plt.legend()
        plt.grid(True)
        ax = plt.gca()
        ax.xaxis.set_major_locator(ticker.MultipleLocator(base=0.5))
        plt.savefig(f'./graphs/{name}.svg')
        plt.savefig(f'./graphs/{name}.png')
        plt.show


    def lengths(self):
        '''
        This will return the amount of samples gathered by a channel
        '''
        return len(self.data)
    





    

        


