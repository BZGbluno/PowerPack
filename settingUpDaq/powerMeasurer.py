from partWeAreMeasuring.partSetUp import Measurements
import threading
import time
import pandas as pd
import numpy as np


class PowerPack:
    '''
    This class is a wrapper and is in charge of running the task of the
    different parts in the computer. It is also in charge of calling their
    functionality.

    Methods:
         __init__(self, numberOfSamplesToGather: int, rateOfSamples: int, ohms):
            -Initializes a new instance of PowerPack

         initializePart(self, name, associatedLines):
            -This will help with initializing each part with its associatedLines
            -Important: The linesNamesMatrix must be in a matrix with 3 rows even if channel names don't
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
    
         start(self):
            -This will start the process of reading power values

         stop(self):
            -This will stop and end the process of reading power values

         makeCSVs(self):
            -This will makes CSV of all the data gathered from the different parts measured

         plot(self):
            -This will plot graphs of all the data gathered from the different parts measured
    
    '''
    def __init__(self, numberOfSamplesToGather: int, rateOfSamples: int, ohms):
        self.numberOfSamplesToGather = numberOfSamplesToGather
        self.rateOfSamples = rateOfSamples
        self.ohms = ohms
        self.registeredParts = []
        self.event = threading.Event()
        self.TotalTime = 0
        self.startTime = 0
        self.stopTime = 0
        self.started = False

    
    def initializePart(self, associatedLines):
        '''
        -This will help with initializing each part with its associatedLines
        -Important: The linesNamesMatrix must be in a matrix with 3 rows even if channel names don't
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
        '''
        try:
            self.PowerPack = Measurements(self.numberOfSamplesToGather, self.rateOfSamples, self.ohms, associatedLines, "PowerPack")
        except Exception as e:
            print(f"Exception occured: {e}")
    
    def start(self):
        '''
        This will spawn a thread for each part of the computer and start the the task
        '''

        self.powerPackThread = threading.Thread(target=self.PowerPack.runTask , args=(self.event,))
        
        
        self.startTime = time.time()
        self.powerPackThread.start()
        self.started = True


        

    def stop(self):
        '''
        This will end the task and join all the threads back together
        '''
        if self.started == False:
            print("Never began the task")
            return
        self.event.set()

        self.powerPackThread.join()
        self.endTime = time.time()
        self.TotalTime = self.endTime - self.startTime
        self.started = False

        

    def makeCSVs(self):
        '''
        This will make a CSV of the data for each part of the computer. Use this
        only after start and stopping the powerpack otherwise no data to be read. 
        '''
        self.PowerPack.makeCSV()


    def plot(self, partsOfInterest, powerCap, verticalAsymtotes=None, pattern=None):
        '''
        This will make a graph of the data for each part of the computer.Use this
        only after start and stopping the powerpack otherwise no data to be read.
        This plot function also takes in a dictionary that has time stamps as keys
        and the name of section you are covering as the value
        '''
        length = self.PowerPack.lengths() - 1
        rate_of_samples = self.rateOfSamples

        times = np.arange(0, length+1) / rate_of_samples
        #print(times)


        for part in partsOfInterest:
            if verticalAsymtotes:
                self.PowerPack.plot(times, part, powerCap, verticalAsymtotes, pattern)
            else:
                self.PowerPack.plot(times, part, powerCap)


    

# Here only for an example
if __name__ == "__main__":
    power_pack = PowerPack(numberOfSamplesToGather=500, rateOfSamples=1000, ohms=0.003)

    # motherboard = [
    #     ["cDAQ2Mod8/ai0","cDAQ2Mod8/ai1","cDAQ2Mod8/ai2","cDAQ2Mod8/ai3"],
    #     ["cDAQ2Mod6/ai0", "cDAQ2Mod6/ai1", "cDAQ2Mod6/ai2", "cDAQ2Mod6/ai3", "cDAQ2Mod6/ai4"],
    #     ["cDAQ2Mod2/ai17", "cDAQ2Mod2/ai18", "cDAQ2Mod2/ai19"]
    # ]


    # cpu = [
    #     [],
    #     [],
    #     ["cDAQ2Mod2/ai4","cDAQ2Mod2/ai5","cDAQ2Mod2/ai6", "cDAQ2Mod2/ai7"]
    # ]

    # 'gpu': [
    #     [],
    #     [],
    #     ["cDAQ2Mod2/ai0","cDAQ2Mod2/ai1","cDAQ2Mod2/ai2", "cDAQ2Mod2/ai3"]
    # ]

    
    # 'disk' : [
    #     ["cDAQ2Mod8/ai7"],
    #     ["cDAQ2Mod6/ai7"],
    #     ["cDAQ2Mod2/ai23"]
    # ]
    parts = {

        'motherboard' : [
            ["cDAQ2Mod8/ai0","cDAQ2Mod8/ai1","cDAQ2Mod8/ai2","cDAQ2Mod8/ai3"],
            ["cDAQ2Mod6/ai0", "cDAQ2Mod6/ai1", "cDAQ2Mod6/ai2", "cDAQ2Mod6/ai3", "cDAQ2Mod6/ai4"],
            ["cDAQ2Mod2/ai17", "cDAQ2Mod2/ai18", "cDAQ2Mod2/ai19"]
        ],

        'cpu' : [
            [],
            [],
            ["cDAQ2Mod2/ai4","cDAQ2Mod2/ai5","cDAQ2Mod2/ai6", "cDAQ2Mod2/ai7"]
        ],

        'gpu': [
            [],
            [],
            ["cDAQ2Mod2/ai0","cDAQ2Mod2/ai1","cDAQ2Mod2/ai2", "cDAQ2Mod2/ai3"]
        ],

    
        'disk' : [
            ["cDAQ2Mod8/ai7"],
            ["cDAQ2Mod6/ai7"],
            ["cDAQ2Mod2/ai23"]
        ]


    }



    #power_pack.initializePart("motherboard", motherboard)
    power_pack.initializePart(parts)
    # power_pack.initializePart("gpu", gpu)
    
    start = time.time()
    # Start measurement task
    power_pack.start()

    # Simulate running for some time
    start = time.time()
    while (time.time() < (start + 5)):
        co = 1

    # Stop measurement task
    power_pack.stop()
    # print(time.time()- start)


    # Plot information
    power_pack.makeCSVs()

    # added = pd.read_csv('./csv/cpuMeasurements.csv')



    # added.data['CPU voltage sum'] = added.data.sum(axis=1)
    # num_rows = len(added)
    # #time is in milliseconds
    # time_between_reads = 1000 / num_rows 


    
    power_pack.plot(['cpu'], powerCap=170)
    # Example of a adding a asymtote that occurs on the 1st second.
    # In this case, it is named cool
    #asymtote = {1:"cool"}
    #power_pack.plot(asymtote)

    print("Main thread exiting")

