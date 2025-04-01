from partSetUp import Measurements
import time
import threading
import pandas as pd

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
    ]


}


part = {


    "gpu": [
        [],
        [],
        ["cDAQ2Mod2/ai0","cDAQ2Mod2/ai1","cDAQ2Mod2/ai2", "cDAQ2Mod2/ai3"]
    ],


}

cool = Measurements(1000, 1000, 0.003, parts, "Power")


# voltMap = cool.getChannelVoltMap()
# print(voltMap)
# print(cool.getTotalLines())

# print(cool.getChannelSamples())


event = threading.Event()



motherboard_thread = threading.Thread(target=cool.runTask, args=(event,))
motherboard_thread.start()
# time.sleep(5)


start = time.time()

while (time.time() < (start + 5)):
    co = 1


event.set()

motherboard_thread.join()


cool.makeCSV()



df = pd.read_csv("./csv/diskgpuMeasurements.csv")

print(f"Testing COL: {df.columns}")

for col in df.columns:
    print(len(df[col]))

