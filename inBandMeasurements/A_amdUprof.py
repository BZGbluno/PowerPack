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





# # adding the path to the global path 
# settingUpDaqPath = os.path.abspath("../uprof/")
# # lineCleaner = os.path.abspath('../uprof/csv-line-remover.sh')
# if os.path.exists(settingUpDaqPath) and settingUpDaqPath not in sys.path:
#     sys.path.append(settingUpDaqPath)

# # if os.path.exists(lineCleaner) and lineCleaner not in sys.path:
# #     sys.path.append(lineCleaner)
# from edittimechart import runner


# run AMDuProf function

type = 'cpu' #type can be cpu or gpu

def runProfiler():
    if (type == 'cpu'): 
        subprocess.run('./profiler.sh')
    else: #if (type == 'gpu')
        subprocess.run('') #INSERT THE name of the script to run the gpu program



# Start measurement task for poth power pack and profiler
profiler = Process(target=runProfiler)


profiler.start()

os.chdir('./benchmarking/')

if (type == 'cpu'): 
    subprocess.run(['python', 'communicationTest.py'])
else: #if (type == 'gpu')
    subprocess.run(['python', 'gputest.py']) #INSERT THE name of the script to run the gpu test
    
os.chdir('../')



# terminate the profiler and join the child process for synchronization
profiler.terminate()
profiler.join()



print(os.getcwd())
time.sleep(10)
# cleaning the information inside main

if (type == 'cpu'): 
    df = runner()
else: 
    #INSERT DATAFRAME FOR GPU test, change line below so df = 'INSERT GPU TEST'()
    df = runner()
print(df)


# plotting the AMDuProf data
plt.plot(df['time_in_seconds'], df['socket0-package-power'], label="Profiler", color ="blue")



# Display the plot
plt.xlabel('Time (seconds)')
plt.ylabel('Power Consumption (Watts)')
plt.legend()
plt.grid(True)
if (type == 'cpu'):  #add timestamp in graph name
    plt.title('Power Consumption of CPU Over Time')
    plt.savefig('./graphs/cpu.png')
else: #if (type == 'gpu')
    plt.title('Power Consumption of GPU Over Time')
    plt.savefig('./graphs/gpu.png')

plt.show()