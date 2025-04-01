from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig 
import torch
import pandas as pd
import re
import threading
import time
import pandas as pd
import numpy as np
import os
import sys
import pdb
import subprocess
from torch.profiler import profile, record_function, ProfilerActivity

# This will be used to setUp PowerPack
settingUpDaqPath = os.path.abspath("../settingUpDaq")
if os.path.exists(settingUpDaqPath) and settingUpDaqPath not in sys.path:
    sys.path.append(settingUpDaqPath)
from powerMeasurer import PowerPack



# Model IDs
# model_id = "meta-llama/Llama-3.2-3B"
# model_id = "meta-llama/Meta-Llama-3-8B-Instruct"
model_id = "meta-llama/Llama-3.2-3B-Instruct"

# Download and load the tokenizer and model
tokenizer = AutoTokenizer.from_pretrained(model_id, padding_side="left")
model = AutoModelForCausalLM.from_pretrained(model_id, 
    device_map="cuda")



'''
The eos token is the end of sequence token indicating that the model should 
stop generating. A pad token is a token that is used to pad sequences to be a 
uniform length
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
    inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True).to(device)
    attention_mask = inputs["attention_mask"]

    start_event = torch.cuda.Event(enable_timing=True)
    end_event = torch.cuda.Event(enable_timing=True)

    # Ensure pad_token_id is set
    outputs = model.generate(inputs["input_ids"], attention_mask=attention_mask, pad_token_id=model.config.pad_token_id)

    with profile(activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA], record_shapes=True, with_flops=True) as prof:
        with record_function("model_inference"):
            start_event.record()
            outputs = model.generate(inputs["input_ids"], attention_mask=attention_mask, pad_token_id=model.config.pad_token_id)
            end_event.record()

    torch.cuda.synchronize()
    execution_time = start_event.elapsed_time(end_event) / 1000

    # Decode the generated tokens into text, skipping special token because we dont want to see special tokens in output Ex: EOS token
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

    total_flops = sum(evt.flops for evt in prof.key_averages() if evt.flops is not None)

    # Compute GFLOPS
    gflops = total_flops / (execution_time * 1e9) if execution_time > 0 else 0

    print(f"Execution Time: {execution_time:.4f} sec")
    print(f"Total FLOPs: {total_flops:.2e}")
    print(f"GFLOPS: {gflops:.2f}")
    return generated_text


# def generate_text_gflops(prompt, duration):
#     '''
#     Function that will tokenize the prompt, and pass it to the model to generate a 
#     response. It returns the model response
#     '''
#     inputs = tokenizer(prompt, return_tensors="pt", padding=True, truncation=True).to(device)
#     attention_mask = inputs["attention_mask"]

#     start_event = torch.cuda.Event(enable_timing=True)
#     end_event = torch.cuda.Event(enable_timing=True)
#     stop = time.time() + duration

#     # Ensure pad_token_id is set
#     outputs = model.generate(inputs["input_ids"], attention_mask=attention_mask, pad_token_id=model.config.pad_token_id)

#     with profile(activities=[ProfilerActivity.CPU, ProfilerActivity.CUDA], record_shapes=True, with_flops=True) as prof:
#         with record_function("model_inference"):
#             start_event.record()
#             outputs = model.generate(inputs["input_ids"], attention_mask=attention_mask, pad_token_id=model.config.pad_token_id)


#             while (time.time() % 1 == 0) & (time.time() < stop): 
#                 end_event.record()
#                 total_flops = sum(evt.flops for evt in prof.key_averages() if evt.flops is not None)

#                 torch.cuda.synchronize()
#                 execution_time = start_event.elapsed_time(end_event) / 1000
#                 gflops = total_flops / (execution_time * 1e9) if execution_time > 0 else 0

#                 print(f"Execution Time: {execution_time:.4f} sec")
#                 print(f"Total FLOPs: {total_flops:.2e}")
#                 print(f"GFLOPS: {gflops:.2f}")

#                 start_event.record()
#             end_event.record()

#     torch.cuda.synchronize()
#     execution_time = start_event.elapsed_time(end_event) / 1000

#     # Decode the generated tokens into text, skipping special token because we dont want to see special tokens in output Ex: EOS token
#     generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

#     # total_flops = sum(evt.flops for evt in prof.key_averages() if evt.flops is not None)

#     # Compute GFLOPS
#     gflops = total_flops / (execution_time * 1e9) if execution_time > 0 else 0

#     print(f"Execution Time: {execution_time:.4f} sec")
#     print(f"Total FLOPs: {total_flops:.2e}")
#     print(f"GFLOPS: {gflops:.2f}")
#     return generated_text


def batch(df, batchSize):

    return np.array_split(df, len(df) // batchSize + (len(df) % batchSize > 0))



def runExperiment(powerCap, parts, dfBatched):

    subprocess.run(["sudo", "nvidia-smi", "-pl", f"{powerCap}"])

    # Initialize PowerPack
    power_pack = PowerPack(numberOfSamplesToGather=2000, rateOfSamples=500, ohms=0.003)
    power_pack.initializePart(parts)

    # Start power measurement
    power_pack.start()

    for counter, x in enumerate(dfBatched):

        print(f"Iteration Count: {counter}")
        p = x['Q'].tolist()
        # generate_text_gflops(p, 30)
        generate_text(p)


    # Stop power measurement
    power_pack.stop()

    # Save results
    power_pack.makeCSVs()


    # Plot results
    power_pack.plot(["cpu", "gpu"])



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
