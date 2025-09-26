from powerMeasurer import Measurements
import time
import threading
import pandas as pd
import numpy as np

parts = {

    # "gpu": [
    #     [],
    #     [],
    #     ["cDAQ2Mod2/ai0","cDAQ2Mod2/ai1","cDAQ2Mod2/ai2", "cDAQ2Mod2/ai3"]
    # ],

    # "disk" : [
    #     ["cDAQ2Mod8/ai7"],
    #     ["cDAQ2Mod6/ai7"],
    #     ["cDAQ2Mod2/ai23"]
    # ]

        "cpu" : [
            [],
            [],
            ["cDAQ2Mod2/ai4","cDAQ2Mod2/ai5","cDAQ2Mod2/ai6", "cDAQ2Mod2/ai7"]
        ]

}

## Test to see how power changes 
def fibonacci(n):
    if n == 1:
        return 0
    if n == 2: 
        return 1
    
    return fibonacci(n - 1) + fibonacci(n - 2)


measures = Measurements(1000, 1000, 0.003, parts, "Power")

event = threading.Event()
motherboard_thread = threading.Thread(target=measures.runTask, args=(event,))
motherboard_thread.start()

print("Test\n")
numbers = [10, 30, 40]

for num in numbers:
   fibonacci(num)


event.set()

motherboard_thread.join()
measures.makeCSV()

df = pd.read_csv("./csv/cpuMeasurements.csv")
print(f"Testing COL: {df.columns}")

for col in df.columns:
    print(len(df[col]))

length = measures.lengths() - 1
rate_of_samples = 1000
times = np.arange(0, length+1) / rate_of_samples

measures.plot(times, "cpu", powerCap=170)
