import nidaqmx
import numpy as np
import time

# Create a task
task = nidaqmx.Task("Measure Using diff")

# Add differential analog input channels (e.g., AI0 and AI8)
task.ai_channels.add_ai_voltage_chan(
    "cDAQ1Mod4/ai0",  # First channel of the differential pair
    terminal_config=nidaqmx.constants.TerminalConfiguration.DIFF
)


task.timing.cfg_samp_clk_timing(
    rate=10, # The sampling rate in samples per second
    sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS,
)


voltageDiff = []
# Start the task
task.start()
start_time = time.time()


try:
    while time.time() - start_time <=10 :  # Continue sampling for 10 seconds
        # Read the voltage value continuously
        voltage = task.read()
        voltageDiff.append(voltage)

        print("Voltage diff measured:", voltage)
except KeyboardInterrupt:
    # Stop the task if Ctrl+C is pressed
    task.stop()
task.close()
