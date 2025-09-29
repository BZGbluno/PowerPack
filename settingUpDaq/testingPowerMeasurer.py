from powerMeasurer import PowerPack
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
    to observe how the GPU power consumption changes
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

    try:
        for i in range(iterations):
            filename = os.path.join(folder, f"test_file_{i}.tmp")
            
            # Write phase, creates file with specified size
            with open(filename, 'w') as file:
                for j in range(file_size_mb):
                    file.write(random_chunk)
            
            # Read phase, reads entire file back
            with open(filename, 'r') as file:
                data = file.read()
                # Force processing of data to ensure actual read operation
                length = len(data)
            
            # Delete phase, remove the file
            os.remove(filename)
    
    finally:
        # Cleanup: remove any remaining test files and directory
        try:
            for file in os.listdir(folder):
                if file.endswith('.tmp'):
                    os.remove(os.path.join(folder, file))
            os.rmdir(folder)
        except (OSError, FileNotFoundError):
            pass

# Create PowerPack instance with measurement parameters
power_pack = PowerPack(numberOfSamplesToGather=1000, rateOfSamples=1000, ohms=0.003)

# Initialize the PowerPack with all parts
power_pack.initializePart(parts)

### Starts measurements ###

# Event to signal when the measurement should stop 
power_pack.start()

# Generate computational load on CPU using the Fibonacci function
numbers = [10, 30, 40]
for num in numbers:
   fibonacci(num)

# Load on GPU
gpu_stress_test(size=100000, iterations=100)

# Load on Disk
disk_stress_test(file_size_mb=100, iterations=10)

# Signal measurement thread to stop after the workload is done 
power_pack.stop()

# Save results 
power_pack.makeCSVs()

# Load measurements for inspection into a dataframe 
df = pd.read_csv("./csv/cpuMeasurements.csv")
print(f"Testing COL: {df.columns}")

for col in df.columns:
    print(len(df[col]))

### Plot the Measurements ###

# Plot CPU power consumption
power_pack.plot(['cpu'], powerCap=170)

# Plot GPU power consumption  
power_pack.plot(['gpu'], powerCap=300)

# Plot disk power consumption
power_pack.plot(['disk'], powerCap=50)