'''
The goals of using the national instrument is to be able to get intial before and after charges
using the national instrument mechanims

Goals for today:
-detect 1 module for detecting 3.3 volts, so we can pass that amount of voltage through the arduino
-name a task after the measurement 3.3
-make a circuit for reading voltage
-make a reading for 3.3 volts using modules 
-retrieve that information
-close the task

-make a circuit, so it can have multiple readings
-
'''

import nidaqmx
import time
import numpy as np

# This is how to create a task, which you can pass it a name
task_name = "Measure_3v3_volts"
task = nidaqmx.task.Task(task_name)


# This task is using 2 different channels to have 2 measurements

task.ai_channels.add_ai_voltage_chan("cDAQ1Mod4/ai0", terminal_config=nidaqmx.constants.TerminalConfiguration.RSE)
task.ai_channels.add_ai_voltage_chan("cDAQ1Mod4/ai8", terminal_config=nidaqmx.constants.TerminalConfiguration.RSE)


task.timing.cfg_samp_clk_timing(
    rate=10, # The sampling rate in samples per second
    sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS, 
)


voltage_readingsBefore = []
voltage_readingsAfter = []

# start the task
task.start()

start_time = time.time()

try:
    while time.time() - start_time <=10 :  # Continue sampling for 10 seconds
        # Read the voltage value continuously
        voltage = task.read()
        voltage_readingsAfter.append(voltage[1])
        voltage_readingsBefore.append(voltage[0])  # Append the voltage reading to the list
        print("Voltage measured:", voltage)
except KeyboardInterrupt:
    # Stop the task if Ctrl+C is pressed
    task.stop()

# Convert the list of voltage readings to a NumPy array
voltage_arrayBefore = np.array(voltage_readingsBefore)
voltage_arrayAfter = np.array(voltage_readingsAfter)


# Close the task
task.close()

np.save("voltage_readingsBefore.npy", voltage_arrayBefore)
np.save("voltage_readingsAfter.npy", voltage_arrayAfter)