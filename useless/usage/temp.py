import nidaqmx
from nidaqmx.constants import TerminalConfiguration, AcquisitionType
import numpy as np
import time
from nidaqmx.stream_readers import AnalogMultiChannelReader

# Constants
NUM_SAMPLES_TO_GATHER = 1000
SAMPLING_RATE = 1000  # Sampling rate in samples per second


def main():
    try:
        # Create a task
        with nidaqmx.Task() as task:
            # Add AI voltage channel (adjust as per your setup)
            task.ai_channels.add_ai_voltage_chan("cDAQ1Mod4/ai0", terminal_config=TerminalConfiguration.DIFF)
            
            # Configure timing for the task
            task.timing.cfg_samp_clk_timing(
                rate=SAMPLING_RATE,  # Sampling rate in samples per second
                sample_mode=AcquisitionType.CONTINUOUS,
                samps_per_chan=NUM_SAMPLES_TO_GATHER
            )



            def callback(task_handle, every_n_samples_event_type, number_of_samples, callback_data):
                try:
                    # Buffer to store the data read from the DAQ device
                    data = np.zeros((1, number_of_samples), dtype=np.float64)
                    
                    # Read data from the task handle
                    reader = AnalogMultiChannelReader(task.in_stream)
                    reader.read_many_sample(data, number_of_samples)
                    
                    # Process the data (e.g., print it or send it to a neural network)
                    print(f"Data shape: {data.shape}")
                    print(f"Data: {data}")
                    
                    # Continue with the callback
                    return 0
                
                except nidaqmx.errors.DaqError as e:
                    print(f"NI-DAQ error in callback: {e}")
                    return -1  # Return -1 to indicate an error
                
                except Exception as ex:
                    print(f"Exception in callback function: {ex}")
                    return -1  # Handle other exceptions gracefully
            
            # Register the callback function
            task.register_every_n_samples_acquired_into_buffer_event(NUM_SAMPLES_TO_GATHER, callback)
            
            # Start the task
            task.start()
            
            # Keep the program running for demonstration
            print("Acquiring data. Press Ctrl+C to stop...")
            
            # Simulate an indefinite loop while data acquisition continues
            while True:
                time.sleep(1)
                
    except KeyboardInterrupt:
        print("User interrupted the program.")
    
    except nidaqmx.errors.DaqError as e:
        print(f"NI-DAQ error: {e}")
    
    except Exception as ex:
        print(f"Exception in main: {ex}")

if __name__ == "__main__":
    main()

