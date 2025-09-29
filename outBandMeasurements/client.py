import os
import sys

settingUpDaqPath = os.path.abspath("../settingUpDaq")
if os.path.exists(settingUpDaqPath) and settingUpDaqPath not in sys.path:
    sys.path.append(settingUpDaqPath)
from powerMeasurer import PowerPack


import socket
import json
import socket
from datetime import datetime
import time

# SERVER_IP = "127.0.0.1" # refers to your own machine 
SERVER_IP = '128.173.55.95'
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
    This is where the client does most of the work. It works by
    first connecting to the server. It then receives a started function
    which is its signal to start measuring. Once the server is done running
    the function, it then recieves a complete signal, which we use to stop
    measuring. At the end, we read from the file the function wrote to gather times
    and return that
    '''
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        
        # connects to the server
        client_socket.connect((ip, port))

        # start power pack
        client_time = time.time() # our start time
        print(client_time)

        power_pack.start()

        client_socket.sendall(message.encode('utf-8'))
        print(f"Message sent to {ip}:{port}")

        # Receive response from the server to start measuring
        startMeasuring = client_socket.recv(32)
        if startMeasuring:
            server_time = startMeasuring.decode('utf-8')

            print(f"Response from server: {server_time}\n\n")
            
            began = str(time.time())
            # power_pack.start()

        # Recieve response from the server to stop measuring
        stopMeasuring = client_socket.recv(16).decode('utf-8')
        print(stopMeasuring)

        server_time = float(server_time)

        
        if stopMeasuring:
            print("The process has been completed, so stop measuring\n\n")
            ended = str(time.time())
            power_pack.stop()
            print(f"\n\n{stopMeasuring}\n\n")
        
        # machineUnderTestTimes = client_socket.recv(512).decode('utf-8')
        
    
    measuringTimes = [began, ended]
    # measuringTimes.append(machineUnderTestTimes)

    calculate_asymptote = server_time - client_time

    print(calculate_asymptote)

    return calculate_asymptote


# Initilize power pack
power_pack = PowerPack(numberOfSamplesToGather=5000, rateOfSamples=50000, ohms=0.003)

# cpu matrix
cpu = [
    [],
    [],
    ["cDAQ1Mod2/ai4", "cDAQ1Mod2/ai5","cDAQ1Mod2/ai6", "cDAQ1Mod2/ai7"]
]

# initalize parts
power_pack.initializePart("cpu")
# power_pack.initializePart("gpu", lineMatrix)
# power_pack.initializePart("motherboard", lineMat)

# send signal to machine under test
vertical = measure(SERVER_IP, SERVER_PORT, "Anyone there?")

print ("Vertical:", vertical)




# Plot information and make the CSV
power_pack.makeCSVs()
power_pack.plot([vertical])  