#!/bin/bash
> gpuPow.csv && watch -n 1 "echo \$(date '+%Y-%m-%d %H:%M:%S'), \$(nvidia-smi --query-gpu=power.draw --format=csv,noheader) >> gpuPow.csv" &>/dev/null
