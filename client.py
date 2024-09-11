from powerMeasurer import PowerPack
import socket
import json
import socket
from datetime import datetime
import time

# SERVER_IP = "127.0.0.1" # refers to your own machine 
SERVER_IP = "172.29.176.187"
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
        client_socket.sendall(message.encode('utf-8'))
        print(f"Message sent to {ip}:{port}")


        # Receive response from the server to start measuring
        startMeasuring = client_socket.recv(16)
        if startMeasuring:
            print(f"Response from server: {startMeasuring.decode('utf-8')}\n\n")
            
            began = str(time.time())
            power_pack.start()

        # Recieve response from the server to stop measuring
        stopMeasuring = client_socket.recv(16).decode('utf-8')
        if stopMeasuring:
            print("The process has been completed, so stop measuring\n\n")
            ended = str(time.time())
            power_pack.stop()
            print(f"\n\n{stopMeasuring}\n\n")
        
    
    times = reader('output.txt')
    with open('./measurements/clientStart.txt', 'a') as f:
        f.write(f"{began}\n")
    with open('./measurements/clientEnd.txt', 'a') as f:
        f.write(f"{ended}\n")
    return times


# Initilize power pack
power_pack = PowerPack(numberOfSamplesToGather=5, rateOfSamples=5, ohms=0.003)

# make matrix with parts
lineMatrix = [[
"cDAQ1Mod4/ai0",
"cDAQ1Mod4/ai3"
],
[],
[]
]
lineMat = [[],["cDAQ1Mod6/ai0"],[]]

# initalize parts
power_pack.initializePart("gpu", lineMatrix)
power_pack.initializePart("motherboard", lineMat)

# start measuring
times = measure(SERVER_IP, SERVER_PORT, "Anyone there?")

# Plot information and make the CSV
power_pack.makeCSVs()
power_pack.plot(times)