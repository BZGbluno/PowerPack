import socket
import json
import csv
import threading
import queue

SERVER_IP = "128.173.242.155" 
SERVER_PORT = 25565
CSV_FILE = "voltage_readings.csv"
BUFFER_SIZE = 100  # Adjust buffer size based on expected data rate and disk I/O speed

# Initialize CSV file with headers
with open(CSV_FILE, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["Voltage Before", "Voltage After"])

# Queue to store incoming data packets
data_queue = queue.Queue()

def write_to_csv():
    """Worker thread to write data from the queue to the CSV file."""
    while True:
        voltage_before, voltage_after = data_queue.get()
        if (voltage_before, voltage_after) == (None, None):
            break  # Stop signal
        with open(CSV_FILE, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([voltage_before, voltage_after])
        data_queue.task_done()

# Start the worker thread
worker_thread = threading.Thread(target=write_to_csv)
worker_thread.start()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((SERVER_IP, SERVER_PORT))
    s.listen()
    print("Server is listening on port", SERVER_PORT)
    
    conn, addr = s.accept()
    print("Connected by", addr)
    with conn:
        while True:
            try:
                data = conn.recv(4096)
                if not data:
                    break
                voltage = json.loads(data.decode('utf-8'))
                voltage_before = voltage[0]
                voltage_after = voltage[1]
                print("Voltage received:", voltage)
                data_queue.put((voltage_before, voltage_after))
            except Exception as e:
                print("Error receiving data:", e)
                break

# Stop the worker thread
data_queue.put((None, None))
worker_thread.join()

print("Data logging completed.")

