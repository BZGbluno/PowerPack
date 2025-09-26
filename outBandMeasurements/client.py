import os
import sys
import socket
import json
import time
from powerMeasurer import PowerPack

# SERVER_IP = "127.0.0.1" # refers to your own machine 
SERVER_IP = "172.29.119.214"
SERVER_PORT = 25565

def reader(file):
    '''
    The goal of this function is to read times written to file 
    by the subprocess function. It then returns this dictionary
    to be used by the client
    '''
    with open(file, 'r') as f:
        data = json.load(f)
    return data


def measure(ip, port, message):
    '''
    Out-of-band measurement:
    - Client signals server to start workload
    - Client begins measuring once server confirms
    - Client stops measuring when server says workload is done
    '''
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((ip, port))

        client_time = time.time()  # when client first connects
        print(f"Client connected at {client_time}")

        # Send message to server to begin workload (CPU/GPU)
        client_socket.sendall(message.encode('utf-8'))
        print(f"Message sent to {ip}:{port}: {message}")

        # Server tells us workload has started
        startMeasuring = client_socket.recv(32)
        if startMeasuring:
            server_time = startMeasuring.decode('utf-8')
            print(f"Response from server (start): {server_time}\n\n")
            began = str(time.time())
            power_pack.start()

        # Server tells us workload has finished
        stopMeasuring = client_socket.recv(16).decode('utf-8')
        print(f"Response from server (stop): {stopMeasuring}")
        if stopMeasuring:
            ended = str(time.time())
            power_pack.stop()
            print("The process has been completed, so stop measuring\n\n")

    measuringTimes = [began, ended]
    calculate_asymptote = float(server_time) - client_time
    print(f"Asymptote (server - client): {calculate_asymptote}")

    return measuringTimes


# Initialize PowerPack
power_pack = PowerPack(numberOfSamplesToGather=5000, rateOfSamples=50000, ohms=0.003)

# CPU line matrix
cpu = [
    [],
    [],
    ["cDAQ1Mod2/ai4", "cDAQ1Mod2/ai5", "cDAQ1Mod2/ai6", "cDAQ1Mod2/ai7"]
]

# GPU line matrix (example channels)
gpu = [
    [],
    [],
    ["cDAQ1Mod2/ai0", "cDAQ1Mod2/ai1"]
]

# Initialize measurement parts
power_pack.initializePart("cpu", cpu)
power_pack.initializePart("gpu", gpu)

# Run out-of-band measurement
vertical = measure(SERVER_IP, SERVER_PORT, "run_cpu")   # or "run_gpu"
print("Vertical:", vertical)

power_pack.makeCSVs()
power_pack.plot(vertical)