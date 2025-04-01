#!/bin/bash

# Ensure the script is executed from the directory containing llama.py
SCRIPT_DIR="$(dirname "$(realpath "$0")")"
cd "$SCRIPT_DIR" || exit

# Define the Python executable and script
PYTHON_EXEC="$(which python3)"
PYTHON_SCRIPT="llama.py"

# Check if the Python script exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo "Error: $PYTHON_SCRIPT not found in $SCRIPT_DIR"
    exit 1
fi

# Define the Nsight Compute report output name
REPORT_NAME="llama_profile_report"

# Run Nsight Compute to profile the Python script
ncu --metrics sm__sass_thread_inst_executed_op_fp32_fma.sum,sm__sass_thread_inst_executed_op_fp64_fma.sum \
    --target-processes all -o "$REPORT_NAME" \
    "$PYTHON_EXEC" "$PYTHON_SCRIPT"