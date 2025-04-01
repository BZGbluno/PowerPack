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
def runProfiler():
    cmd = './profiler.sh'
    subprocess.run(cmd)



# Start measurement task for poth power pack and profiler
profiler = Process(target=runProfiler)


profiler.start()

os.chdir('./benchmarking/')
subprocess.run(['python', 'communicationTest.py'])
os.chdir('../')



# terminate the profiler and join the child process for synchronization
profiler.terminate()
profiler.join()



print(os.getcwd())
time.sleep(10)
# cleaning the information inside main
df = runner()
print(df)


# plotting the AMDuProf data
plt.plot(df['time_in_seconds'], df['socket0-package-power'], label="Profiler", color ="blue")



# Display the plot
plt.xlabel('Time (seconds)')
plt.ylabel('Power Consumption (Watts)')
plt.title('Power Consumption of CPU Over Time')
plt.legend()
plt.ylim(0, 100)
plt.grid(True)
plt.savefig('./graphs/cpu.png')
plt.show()