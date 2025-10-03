import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
import subprocess
import time
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig 
from streamer import TimeLoggingStreamer
from datetime import datetime

# This will be used to setUp PowerPack
settingUpDaqPath = os.path.abspath("../../settingUpDaq")
if os.path.exists(settingUpDaqPath) and settingUpDaqPath not in sys.path:
    sys.path.append(settingUpDaqPath)
from powerMeasurer import PowerPack



model_id = "meta-llama/Llama-3.2-3B-Instruct"

# Download and load the tokenizer and model
tokenizer = AutoTokenizer.from_pretrained(model_id, padding_side="left")
model = AutoModelForCausalLM.from_pretrained(model_id, 
    device_map="cuda")


'''
The eos token is the end of sequence token indicating that the model should 
stop generating. A pad token is a token that is used to pad sequences to be a 
uniform length.
'''
tokenizer.pad_token = tokenizer.eos_token  # Set pad token as eos token
model.config.pad_token_id = tokenizer.pad_token_id  # Ensure the model is aware


# Ensure the model is in evaluation mode because we are not training
model.eval()

# Looking to leverage cuda if possible
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def generate_text(prompt):
    '''
    Function that will tokenize the prompt, and pass it to the model to generate a 
    response. It returns the model response
    '''
    # started = datetime.now()
    streamer = TimeLoggingStreamer(tokenizer)
    inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True).to(device)
    doneTokenizer = time.time()
    attention_mask = inputs["attention_mask"]

    started = datetime.now()
    # Ensure pad_token_id is set
    model.generate(inputs["input_ids"], streamer=streamer,attention_mask=attention_mask, pad_token_id=model.config.pad_token_id)
    doneGenerating = time.time()

    return (streamer.getFirstTimeStamp()-started).total_seconds(), streamer.getTimesStamps(), (doneTokenizer, doneGenerating)


def runExperiment(powerCap, parts, dfBatched):

    timesArr = []
    subprocess.run(["sudo", "nvidia-smi", "-pl", f"{powerCap}"])


    # Initialize PowerPack
    power_pack = PowerPack(numberOfSamplesToGather=2000, rateOfSamples=500, ohms=0.003)
    power_pack.initializePart(parts)
    power_pack.start()


    # latency times
    latencyTimes = []

    for x in range(len(dfBatched)):

        #print(f"Iteration Count: {counter}")
        p = dfBatched[x]['question'].tolist()
        # generate_text_gflops(p, 30)

        #Todo
        
        latency, times, asym = generate_text(p)
        timesArr.append(times)
        latencyTimes.append(latency)

    
    # Stop power measurement
    power_pack.stop()

    # Save results
    power_pack.makeCSVs(f"{powerCap}")

    # Save latencyTimes to a DataFrame
    latencyDf = pd.DataFrame(latencyTimes, columns=["Latency"])
    latencyDf.to_csv(f"latency_times{powerCap}.csv", index=False)

    # Save timesArr to a DataFrame
    # Flatten nested lists or make each row a list of time deltas
    timesDf = pd.DataFrame(timesArr)
    timesDf.to_csv(f"generation_times{powerCap}.csv", index=False)

    # plot the graphs
    power_pack.plot(["gpu"], powerCap)


def batch(df, batchSize):

    return np.array_split(df, len(df) // batchSize + (len(df) % batchSize > 0))


def main():
    parts = {
        'gpu': [
            [],
            [],
            ["cDAQ2Mod2/ai0","cDAQ2Mod2/ai1","cDAQ2Mod2/ai2", "cDAQ2Mod2/ai3"]
        ]
    }

    datasetPath = "../datasets/llm_inference/testGsm8k.csv"

    

    df = pd.read_csv(datasetPath)
    powerCapList = [110]

    for powerCap in powerCapList:
        batchedDf = batch(df, 16)
        runExperiment(powerCap, parts, batchedDf)

       


if __name__ == "__main__":
    main()


