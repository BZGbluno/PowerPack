import sys
import os
import time
import pdb
from multiprocessing import Process, Event
import subprocess
import pandas as pd
from uprof.edittimechart import runner
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np
from sklearn.model_selection import TimeSeriesSplit

# This will be used to setUp PowerPack
settingUpDaqPath = os.path.abspath("../settingUpDaq")
if os.path.exists(settingUpDaqPath) and settingUpDaqPath not in sys.path:
    sys.path.append(settingUpDaqPath)
from powerMeasurer import PowerPack


PowerPack = PowerPack(numberOfSamplesToGather=2000, rateOfSamples=500, ohms=0.003)

cpu = [
        [],
        [],
        ["cDAQ2Mod2/ai4","cDAQ2Mod2/ai5","cDAQ2Mod2/ai6", "cDAQ2Mod2/ai7"]
    ]

gpu = [
        [],
        [],
        ["cDAQ2Mod2/ai0","cDAQ2Mod2/ai1","cDAQ2Mod2/ai2", "cDAQ2Mod2/ai3"]
    ]

disk = [
        ["cDAQ2Mod8/ai7"],
        ["cDAQ2Mod6/ai7"],
        ["cDAQ2Mod2/ai22"]
    ]

motherboard = [
    ["cDAQ2Mod8/ai0","cDAQ2Mod8/ai1","cDAQ2Mod8/ai2","cDAQ2Mod8/ai3"],
    ["cDAQ2Mod6/ai0", "cDAQ2Mod6/ai1", "cDAQ2Mod6/ai2", "cDAQ2Mod6/ai3", "cDAQ2Mod6/ai4"],
    ["cDAQ2Mod2/ai17", "cDAQ2Mod2/ai18", "cDAQ2Mod2/ai19"]
]


# PowerPack.initializePart("gpu", gpu)
PowerPack.initializePart("cpu", cpu)
PowerPack.initializePart("disk", disk)
# PowerPack.initializePart("motherboard", motherboard)


PowerPack.start()

time.sleep(5)
PowerPack.stop()
PowerPack.makeCSVs()
PowerPack.plot()

