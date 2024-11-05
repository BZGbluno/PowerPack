import subprocess
import os
import time
import signal

startTime = time.time()
# 5 seconds of doing nothing
time.sleep(5)

# communication loop that will have 5 spikes
for _ in range(0,5):

    # Start the process in the background
    process = subprocess.Popen(['./cpuburn'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Get the PID of the process
    print(f"Process ID (PID): {process.pid}")

    # Wait for 15 seconds
    time.sleep(15)

    # Kill the process after 20 seconds
    os.kill(process.pid, signal.SIGTERM)

    # Wait for 5 seconds
    time.sleep(5)


    print(f"Process {process.pid} has been terminated.")

print(f"end Time is: {time.time()- startTime}")