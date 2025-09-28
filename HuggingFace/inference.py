import torch 
from transformers import AutoTokenizer, AutoModelForCausalLM
import time 

# Set up CUDA device 
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

# Check that CUDA is working 
if torch.cuda.is_available():
    print(f"CUDA device name: {torch.cuda.get_device_name()}")
    print(f"CUDA memory available: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
else:
    print("CUDA not available, using CPU")

# Load model and tokenizer into memory
model_name = "microsoft/DialoGPT-small" # picked a random model 
model = AutoModelForCausalLM.from_pretrained(model_name)

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_name)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token 

# Move Model to CUDA device 
model = model.to(device)
model.eval() # set to evaluation 

# Check GPU memory usage
if torch.cuda.is_available():
    print(f"GPU memory used: {torch.cuda.memory_allocated() / 1024**2:.1f} MB")

def run_inference(text_input):
    """Run inference with the loaded model"""
    print(f"\nInput: {text_input}")
    
    # Converts text to tokens, returns PyTorch sensors, and moves input to GPU
    inputs = tokenizer.encode(text_input, return_tensors="pt", padding=True).to(device)
    
    # Run inference
    start_time = time.time()
    with torch.no_grad(): # disable gradient calculations to be faster
        outputs = model.generate(
            inputs,
            max_length=inputs.shape[1] + 100,
            temperature=0.8,
            do_sample=True,
            pad_token_id=tokenizer.eos_token_id
        ) 
        # Generates text
        # Higher temperature = more creative 
    
    inference_time = time.time() - start_time
    
    # Decode output back into text
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    print(f"Output: {response}")
    print(f"Inference time: {inference_time:.3f} seconds")
    
    return response

# 5. Test the inference
if __name__ == "__main__":
    # Test with some sample inputs
    test_inputs = [
        "Hello, how are you?",
        "What is your name?",
        "Tell me about your day"
    ]
    
    for test_input in test_inputs:
        run_inference(test_input)
        print("-" * 50)
    
    # Show final GPU memory usage
    if torch.cuda.is_available():
        print(f"\nFinal GPU memory used: {torch.cuda.memory_allocated() / 1024**2:.1f} MB")