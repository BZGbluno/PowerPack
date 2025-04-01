import subprocess
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from powerMeasurer import PowerPack  # Import your PowerPack class




# Define benchmarking parameters
# BENCHMARK_COMMAND = "/Desktop/cuda-samples/bin/x86_64/linux/release/matrixMul"  # Update with your actual script path
# TEST_DURATION = 10 # Adjust based on your test duration

# Define parts to monitor
parts = {

        # 'motherboard' : [
        #     ["cDAQ2Mod8/ai0","cDAQ2Mod8/ai1","cDAQ2Mod8/ai2","cDAQ2Mod8/ai3"],
        #     ["cDAQ2Mod6/ai0", "cDAQ2Mod6/ai1", "cDAQ2Mod6/ai2", "cDAQ2Mod6/ai3", "cDAQ2Mod6/ai4"],
        #     ["cDAQ2Mod2/ai17", "cDAQ2Mod2/ai18", "cDAQ2Mod2/ai19"]
        # ],

        'cpu' : [
            [],
            [],
            ["cDAQ2Mod2/ai4","cDAQ2Mod2/ai5","cDAQ2Mod2/ai6", "cDAQ2Mod2/ai7"]
        ],

        'gpu': [
            [],
            [],
            ["cDAQ2Mod2/ai0","cDAQ2Mod2/ai1","cDAQ2Mod2/ai2", "cDAQ2Mod2/ai3"]
        ],

    
        # 'disk' : [
        #     ["cDAQ2Mod8/ai7"],
        #     ["cDAQ2Mod6/ai7"],
        #     ["cDAQ2Mod2/ai23"]
        # ]


    }

# Initialize PowerPack
power_pack = PowerPack(numberOfSamplesToGather=2000, rateOfSamples=500, ohms=0.003)
power_pack.initializePart(parts)

# Start power measurement
power_pack.start()
time.sleep(2)  # Ensure measurements start before the test

# Run the benchmark
for run in range(50):
    # print(f"Running benchmark {run + 1}/{NUM_RUNS}")
    start_time = time.time()
    subprocess.run(['./matrixMul', '-wA=1024', '-wB=1024', '-hA=1024', '-hB=1024'])
    end_time = time.time()
    # print(f"Run {run + 1} completed in {end_time - start_time:.2f} seconds")

# Stop power measurement
power_pack.stop()

# Save results
power_pack.makeCSVs()

# Print test duration
#print(f"Benchmark completed in {end_time - start_time:.2f} seconds")

# Plot results
power_pack.plot(["cpu", "gpu", "disk", "motherboard"])
# power_pack.plot(["gpu"])\