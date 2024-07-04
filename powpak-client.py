import nidaqmx
import time
import socket
import json
import threading
import queue
# Network setup
SERVER_IP = "172.21.222.62"  # Replace with your server's IP address
SERVER_PORT = 25565

# Queue to store voltage readings
data_queue = queue.Queue()
# Sending Data Thread
def send_data_to_server(sock):
    while True:
        voltage = data_queue.get()
        if voltage is None:
            break
        try:
            sock.sendall(json.dumps(voltage).encode('utf-8'))
            print("Voltage sent:", voltage)
        except Exception as e:
            print("Failed to send data to server:", e)
        data_queue.task_done()

# Data acquisition thread
def acquire_data(task):
    try:
        while True:  # Run indefinitely
            voltage = task.read()
            data_queue.put(voltage)
            print("Voltage measured:", voltage)
            time.sleep(0.1)  # Adjust the sleep time based on your needs

    except KeyboardInterrupt:
        data_queue.put(None)  # Signal to stop the sending thread

# Create and start the task
task_name = "Measure_3v3_volts"
task = nidaqmx.task.Task(task_name)
task.ai_channels.add_ai_voltage_chan("cDAQ1Mod4/ai8", min_val=0, max_val=3.3)
task.ai_channels.add_ai_voltage_chan("cDAQ1Mod4/ai0", min_val=0, max_val=3.3)
task.timing.cfg_samp_clk_timing(rate=10, sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)
task.start()

# Establish a persistent connection to the server
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect((SERVER_IP, SERVER_PORT))
    
    # Start the data sending thread
    sending_thread = threading.Thread(target=send_data_to_server, args=(sock,))
    sending_thread.start()

    # Start the data acquisition thread
    acquire_data_thread = threading.Thread(target=acquire_data, args=(task,))
    acquire_data_thread.start()

    # Wait for the data acquisition thread to finish
    acquire_data_thread.join()
    
    # Stop the task
    task.stop()
    task.close()

    # Wait for the data sending thread to finish
    sending_thread.join()
