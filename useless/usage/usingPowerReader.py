import nidaqmx
import sys
import time
import numpy as np
import threading
from nidaqmx.constants import TerminalConfiguration
from nidaqmx.stream_readers import PowerMultiChannelReader
from graphPlotting import plotGraphs

# Constants
THREEVOLTS = 3.3
FIVEVOLTS = 5
TWELVEVOLTS = 12
NUM_SAMPLES_TO_GATHER = 10
OHMS = 0.003  # Ohm value for shunt resistor
line1 = []
line2 = []
line3 = []
times = []
tiempo = 10

def run_nidaq_task(samplingRate, stop_event):
    try:
        # Create a task
        task = nidaqmx.Task("Measure Total Power Consumption")

        # Channels for power measurements
        task.ai_channels.add_ai_power_chan("cDAQ1Mod4/ai0", "cDAQ1Mod4/ai8")  # Voltage and current for 3.3V
        # task.ai_channels.add_ai_power_chan("cDAQ1Mod4/ai2", "cDAQ1Mod4/ai3")  # Voltage and current for 5V
        # task.ai_channels.add_ai_power_chan("cDAQ1Mod4/ai4", "cDAQ1Mod4/ai5")  # Voltage and current for 12V

        # Setting up the sampling rates
        task.timing.cfg_samp_clk_timing(
            rate=samplingRate,  # The sampling rate in samples per second
            sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS,
            samps_per_chan=NUM_SAMPLES_TO_GATHER
        )
        reader = PowerMultiChannelReader(task.in_stream)

        # Define a callback function
        def callback(task_handle, every_n_samples_event_type, number_of_samples, callback_data):
            try:
                if not isinstance(task, nidaqmx.Task):
                    print("Task is not a valid nidaqmx.Task")
                    return -1
                
                voltage = np.zeros((1, number_of_samples), dtype=np.float64)
                current = np.zeros((1, number_of_samples), dtype=np.float64)

                # Read the data
                reader.read_many_sample(voltage, current, number_of_samples)

                # Process the data
                for x in range(number_of_samples):
                    power_3v3 = voltage[0][x] * current[0][x]
                    # power_5v = voltage[1][x] * current[1][x]
                    # power_12v = voltage[2][x] * current[2][x]
                    
                    line1.append(power_3v3)
                    # line2.append(power_5v)
                    # line3.append(power_12v)

                return 0
            except nidaqmx.errors.DaqError as e:
                print(f"NI-DAQ error in callback: {e}")
                return -1
            except Exception as ex:
                print(f"Exception in callback function: {ex}")
                return -1

        # Register the callback function
        task.register_every_n_samples_acquired_into_buffer_event(NUM_SAMPLES_TO_GATHER, callback)

        # Start the task
        task.start()

        # Keep the task running until the stop event is set
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

def main_task(stop_event):
    try:
        print("Main thread is running...")
        time.sleep(tiempo) 
    except KeyboardInterrupt:
        print("Main task interrupted by user")
    finally:
        print("The task has ended")

def main():
    if len(sys.argv) != 2:
        print("This function needs 1 argument: samplingRate")
        sys.exit(1)

    samplingRate = int(sys.argv[1])

    # Create a stop event to signal threads to stop
    stop_event = threading.Event()

    # Create and start the NI-DAQ thread
    nidaq_thread = threading.Thread(target=run_nidaq_task, args=(samplingRate, stop_event))
    nidaq_thread.start()

    # Run the main task in the main thread
    try:
        main_task(stop_event)
    except KeyboardInterrupt:
        print("Stopping all tasks...")

    # Signal the NI-DAQ thread to stop
    stop_event.set()

    # Wait for the NI-DAQ thread to finish
    nidaq_thread.join()
    print(len(line1))
    passedTime = 0
    times.append(passedTime)
    for x in range(0, len(line1) - 1):
        passedTime += (1 / samplingRate)
        times.append(passedTime)
    print(times)

    plotGraphs(times, line1, line2, line3)

if __name__ == "__main__":
    main()
