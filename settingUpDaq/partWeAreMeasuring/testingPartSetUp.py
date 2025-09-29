from partSetUp import Measurements
import time
import threading
import pandas as pd
import numpy as np
import torch 
import os
import random
import string

"""
Dictionary representing the PowerPack hardware parts and their associated channels. 
Note that each key corresponds to a type of hardware component. Each value is 
a list of sublists, with identifiers for the input channels on that part. 
These values all align with the cardboard pieces. 
"""
parts = {

    "gpu": [
        [],
        [],
        ["cDAQ2Mod2/ai0","cDAQ2Mod2/ai1","cDAQ2Mod2/ai2", "cDAQ2Mod2/ai3"]
    ],

    "disk" : [
        ["cDAQ2Mod8/ai7"],
        ["cDAQ2Mod6/ai7"],
        ["cDAQ2Mod2/ai23"]
    ],

        "cpu" : [
            [],
            [],
            ["cDAQ2Mod2/ai4","cDAQ2Mod2/ai5","cDAQ2Mod2/ai6", "cDAQ2Mod2/ai7"]
        ]
}

## Test to see how power changes 
def fibonacci(n):
    """
    Uses recursion to compute the Nth fibonacci number. Without optimization, this 
    generates a significate CPU load. Used here to simulate a computationally intensive 
    workload to observe how CPU power consumption changes 
    """
    if n == 1:
        return 0
    if n == 2: 
        return 1
    
    return fibonacci(n - 1) + fibonacci(n - 2)

def gpu_stress_test(size=10000, iterations=100, device="cuda"):
    """"
    Performs a GPU-intensive workload by executing math operations under a heavy load
    to obeserve how the GPU power consumption changes
    """
    x = torch.rand(size, device=device)
    for _ in range(iterations):
        x = torch.sqrt(x) * torch.sin(x) + torch.log(x+1)

def disk_stress_test(file_size_mb=100, iterations=10, folder="./disk_test"):
    """ 
    Performs a disk-intensive workload by writing, reading, and deleting large files
    to observe how the Disk power consumption changes
    """
    os.makedirs(folder, exist_ok=True)

    # Generate random data to write 
    chunk_size = 1024 * 1024  # 1MB
    random_chunk = ''.join(random.choices(string.ascii_letters + string.digits, k=chunk_size))

    for i in range(iterations):
            filename = os.path.join(folder, f"test_file_{i}.tmp")
            
            # Write phase, creates file with specified size
            with open(filename, 'w') as file:
                for i in range(file_size_mb):
                    file.write(random_chunk)
            
            # Read phase, reads entire file back
            with open(filename, 'r') as file:
                data = file.read()
                # Force processing of data to ensure actual read operation
                length = len(data)
            
            # Delete phase, remove the file
            os.remove(filename)

# Creates a Measurements object 
measures = Measurements(1000, 1000, 0.003, parts, "Power")

### Starts measurements in a separate thread ###

# Event to signal when the measurement should stop 
event = threading.Event()
motherboard_thread = threading.Thread(target=measures.runTask, args=(event,))
# Begins power measurements concurrently 
motherboard_thread.start()

# Generate computational load on CPU using the Fibonacci function
numbers = [10, 30, 40]
for num in numbers:
   fibonacci(num)

# Load on GPU
gpu_stress_test(size=100000, iterations=100)

# Load on Disk
disk_stress_test(file_size_mb=100, iterations=10)

# Signal measurement thread to stop after the workload is done 
event.set()

# Ensure that the measurement thread completes and save results to a CSV
motherboard_thread.join()
measures.makeCSV()

# Load measurements for inspection into a dataframe 
df = pd.read_csv("./csv/cpuMeasurements.csv")
print(f"Testing COL: {df.columns}")

for col in df.columns:
    print(len(df[col]))

### Plot the Measurements ###
length = measures.lengths() - 1
rate_of_samples = 1000
times = np.arange(0, length+1) / rate_of_samples

measures.plot(times, "cpu", powerCap=170)
