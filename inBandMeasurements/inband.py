import sys
import os
import time
import pdb

settingUpDaqPath = os.path.abspath("../settingUpDaq")
if os.path.exists(settingUpDaqPath) and settingUpDaqPath not in sys.path:
    sys.path.append(settingUpDaqPath)

from powerMeasurer import PowerPack

print(sys.path)

#print(os.getcwd())

#pdb.set_trace()
Power = PowerPack(numberOfSamplesToGather=100, rateOfSamples=1000, ohms=0.003)

motherboard = [
        ["cDAQ2Mod8/ai0","cDAQ2Mod8/ai1","cDAQ2Mod8/ai2","cDAQ2Mod8/ai3"],
        ["cDAQ2Mod6/ai0", "cDAQ2Mod6/ai1", "cDAQ2Mod6/ai2", "cDAQ2Mod6/ai3", "cDAQ2Mod6/ai4"],
        ["cDAQ2Mod2/ai17", "cDAQ2Mod2/ai18", "cDAQ2Mod2/ai19"]
    ]

gpu = [
        [],
        [],
        ["cDAQ2Mod2/ai0","cDAQ2Mod2/ai1","cDAQ2Mod2/ai2"]
    ]

cpu = [
        [],
        [],
        ["cDAQ2Mod2/ai4","cDAQ2Mod2/ai5","cDAQ2Mod2/ai6", "cDAQ2Mod2/ai7"]
    ]

disk = [
        ["cDAQ2Mod8/ai7"],
        ["cDAQ2Mod6/ai7"],
        ["cDAQ2Mod2/ai22"]
    ]

Power.initializePart("motherboard", motherboard)
Power.initializePart("disk", disk)
Power.initializePart("cpu", cpu)


start = time.time()
# Start measurement task
Power.start()


# Simulate running for some time
time.sleep(10)

# Stop measurement task
Power.stop()

Power.makeCSVs()




#./AMDuProfCLI  timechart --interval 100 --duration 10 --event socket=0,power -o /home/bruno//.AMDuProf/AMDuProf/