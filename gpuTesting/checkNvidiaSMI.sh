#!/bin/bash

#less ~/.bash_history
#nvidia-smi -lgc 300,1000
#nvidia-smi -q -d CLOCK
#nvidia-smi -q -d POWER
#sudo nvidia-smi -pl 200


nvidia-smi

MATMUL_PATH=~/Desktop/cuda-samples/bin/x86_64/linux/release


for (( i=0; i<100; i+=1 )) do 
    $MATMUL_PATH/./matrixMul -wA=1024 -wB=1024 -hA=1024 -hB=1024
    nvidia-smi
    sleep 0.1
done



nvidia-smi