import requests
import json
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import time
import os
import sys
import pandas as pd
import subprocess
import pylikwid

# This will be used to setUp PowerPack
settingUpDaqPath = os.path.abspath("../settingUpDaq")
if os.path.exists(settingUpDaqPath) and settingUpDaqPath not in sys.path:
    sys.path.append(settingUpDaqPath)
from powerMeasurer import PowerPack



# Define the URL for the local Ollama server (assuming it's running locally)
url = "http://localhost:11434/api/generate"



def parse_timestamp(ts):
    ts = ts.rstrip("Z")
    ts_micro = ts[:23]
    return datetime.strptime(ts_micro, "%Y-%m-%dT%H:%M:%S.%f")




def generate_text(questions):
    

    combinedPrompt = "\n".join(f"{q}" for q in questions)
    # print(combinedPrompt)

    times = []
    # Create a payload with the model and the input query
    data = {
    "model": "llama3.1", # Specify the model name
    "prompt": combinedPrompt,
    "stream": True
    }



    response = requests.post(url, json=data, stream=True)
    if response.status_code == 200:
        for chunk in response.iter_lines():
            if chunk:
                data = json.loads(chunk.decode("utf-8"))
                # print(data)
                times.append(data['created_at'])
    else:
        print(f"Error: {response.status_code}")
    
    return times



def batch(df, batchSize):

    return np.array_split(df, len(df) // batchSize + (len(df) % batchSize > 0))



def makeHist(powerCap, times, start, end):

        first = parse_timestamp(times[0])
        indexs = []
        tiempos = []
        words = []
        for index, element in enumerate(times):
            if index > 0:
                tiempo = (parse_timestamp(element)- first).total_seconds()
                first = parse_timestamp(element)
                tiempos.append(tiempo)
                words.append(1/tiempo)
                indexs.append(index)

        print(f"Overall Average: {len(times) / (end-start)}")
        print(np.mean(words))
        plt.hist(words, bins=8)
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d %H:%M:%S")
        plt.savefig(f'./graphs/{powerCap}{date_str}.png')


def runExperiment(powerCap, parts, dfBatched):

    
    subprocess.run(["sudo", "nvidia-smi", "-pl", f"{powerCap}"])
    allTimes = []
    # Initialize PowerPack
    power_pack = PowerPack(numberOfSamplesToGather=2000, rateOfSamples=500, ohms=0.003)
    power_pack.initializePart(parts)

    # Start power measurement
    power_pack.start()

    start = time.time()
    for counter, x in enumerate(dfBatched):

        print(f"Iteration Count: {counter}")
        p = x['Q'].tolist()
        # generate_text_gflops(p, 30)


        # runTimes = generate_text(p)
        runTimes = generate_text(p)


        allTimes = allTimes + runTimes

    end = time.time()
    # Stop power measurement
    power_pack.stop()

    # Save results
    power_pack.makeCSVs()


    # Plot results
    power_pack.plot(["cpu", "gpu"])

    makeHist(powerCap, allTimes, start, end)




def main():

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

    # Specify the path to your TSV file
    file_path = '~/Downloads/mgsm_en.tsv'


    # Read the TSV file into a pandas DataFrame
    df = pd.read_csv(file_path, sep='\t', names=['Q', 'A'])

    batchedDf = batch(df, 1)

    runExperiment(250, parts, batchedDf)
    # runExperiment(200, parts, batchedDf)
    # runExperiment(150, parts, batchedDf)



if __name__ == "__main__":
    main()





# Command: ollama run llama3.2:1b
# export CUDA_VISIBLE_DEVICES=0 # For GPU usage