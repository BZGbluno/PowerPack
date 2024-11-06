from partWeAreMeasuring.partSetUp import Measurements
import threading
import time
import pandas as pd


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
        self.threads = []
        self.TotalTime = 0
        self.startTime = 0
        self.stopTime = 0
        self.started = False

    
    def initializePart(self, name, associatedLines):
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
        if (len(self.registeredParts) < 4):   
            if name == 'gpu':
                self.gpu = Measurements(self.numberOfSamplesToGather, self.rateOfSamples, self.ohms, associatedLines, name)
                self.gpu_thread = None
                self.registeredParts.append(self.gpu)
            elif name == 'motherboard':
                self.motherboard = Measurements(self.numberOfSamplesToGather, self.rateOfSamples, self.ohms, associatedLines, name)
                self.motherboard_thread = None
                self.registeredParts.append(self.motherboard)
            elif name == 'cpu':
                self.cpu = Measurements(self.numberOfSamplesToGather, self.rateOfSamples, self.ohms, associatedLines, name)
                self.cpu_thread = None
                self.registeredParts.append(self.cpu)
            elif name == 'disk':
                self.disk = Measurements(self.numberOfSamplesToGather, self.rateOfSamples, self.ohms, associatedLines, name)
                self.disk_thread = None
                self.registeredParts.append(self.disk)
            else:
                print("No valid part names were entered: enter (gpu, motherboard, cpu, disk)")
        else:
            print("You have exceeded amount of parts to register")

    
    def start(self):
        '''
        This will spawn a thread for each part of the computer and start the the task
        '''
        if len(self.registeredParts) == 0:
            print("There are no registered parts")
            return 
        for part in self.registeredParts:
            if part.getName() == "gpu":
                gpu_thread = threading.Thread(target=self.gpu.runTask, args=(self.event,))
                self.threads.append(gpu_thread)

            elif part.getName() == "cpu":
                cpu_thread = threading.Thread(target=self.cpu.runTask, args=(self.event,))
                self.threads.append(cpu_thread)

            elif part.getName() == "motherboard":
                motherboard_thread = threading.Thread(target=self.motherboard.runTask, args=(self.event,))
                self.threads.append(motherboard_thread)
            elif part.getName() == "disk":

                disk_thread = threading.Thread(target=self.disk.runTask, args=(self.event,))
                self.threads.append(disk_thread)
        
        self.startTime = time.time()
        for thread in self.threads:
            thread.start()
        self.started = True
        # began = str(time.time())
        # with open('./measurements/startFunc.txt', 'a') as f:
        #     f.write(f"{began}\n")

        

    def stop(self):
        '''
        This will end the task and join all the threads back together
        '''
        if self.started == False:
            print("Never began the task")
            return
        self.event.set()
        for thread in self.threads:
            thread.join()
        self.endTime = time.time()
        self.TotalTime = self.endTime - self.startTime
        self.started = False

        

    def makeCSVs(self):
        '''
        This will make a CSV of the data for each part of the computer. Use this
        only after start and stopping the powerpack otherwise no data to be read. 
        '''
        for part in self.registeredParts:
            part.makeCSV()


    def plot(self, verticalAsymtotes=None):
        '''
        This will make a graph of the data for each part of the computer.Use this
        only after start and stopping the powerpack otherwise no data to be read.
        This plot function also takes in a dictionary that has time stamps as keys
        and the name of section you are covering as the value
        '''
        # #print(self.registeredParts[0].lengths())
        # times = []
        # passedTime = 0
        # times.append(passedTime)
        # for _ in range(0, self.registeredParts[0].lengths()-1):
        #     passedTime += (1/self.rateOfSamples)
        #     times.append(passedTime)
        length = self.registeredParts[0].lengths() - 1
        rate_of_samples = self.rateOfSamples

        times = np.arange(length + 1) / rate_of_samples


        for part in self.registeredParts:
            if verticalAsymtotes:
                part.plot(times, verticalAsymtotes)
            else:
                part.plot(times)


    

# Here only for an example
if __name__ == "__main__":
    power_pack = PowerPack(numberOfSamplesToGather=6250, rateOfSamples=62500, ohms=0.003)

    motherboard = [
        ["cDAQ2Mod8/ai0","cDAQ2Mod8/ai1","cDAQ2Mod8/ai2","cDAQ2Mod8/ai3"],
        ["cDAQ2Mod6/ai0", "cDAQ2Mod6/ai1", "cDAQ2Mod6/ai2", "cDAQ2Mod6/ai3", "cDAQ2Mod6/ai4"],
        ["cDAQ2Mod2/ai17", "cDAQ2Mod2/ai18", "cDAQ2Mod2/ai19"]
    ]

    gpu = [
        [],
        [],
        ["cDAQ2Mod2/ai0","cDAQ2Mod2/ai1","cDAQ2Mod2/ai2"]
    ]

    cpu = [
        [],
        [],
        ["cDAQ2Mod2/ai4","cDAQ2Mod2/ai5","cDAQ2Mod2/ai6", "cDAQ2Mod2/ai7"]
    ]

    disk = [
        ["cDAQ2Mod8/ai7"],
        ["cDAQ2Mod6/ai7"],
        ["cDAQ2Mod2/ai22"]
    ]



    #power_pack.initializePart("motherboard", motherboard)
    # power_pack.initializePart("disk", disk)
    power_pack.initializePart("cpu", cpu)
    
    start = time.time()
    # Start measurement task
    power_pack.start()

    # Simulate running for some time
    time.sleep(3)

    # Stop measurement task
    power_pack.stop()
    # print(time.time()- start)


    # Plot information
    power_pack.makeCSVs()

    added = pd.read_csv('cpuMeasurements.csv')
    added.data['CPU voltage sum'] = added.data.sum(axis=1)
    num_rows = len(added)
    #time is in milliseconds
    time_between_reads = 1000 / num_rows 


    
    power_pack.plot()
    # Example of a adding a asymtote that occurs on the 1st second.
    # In this case, it is named cool
    #asymtote = {1:"cool"}
    #power_pack.plot(asymtote)

    print("Main thread exiting")

