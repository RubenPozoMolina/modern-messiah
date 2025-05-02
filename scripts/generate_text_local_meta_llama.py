from transformers import pipeline, BitsAndBytesConfig
import torch

# Configure 4-bit quantization
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True
)

messages = [
    {"role": "system", "content": "You are a pirate chatbot who always responds in pirate speak!"},
    {"role": "user", "content": "Who are you?"},
]

# Use 4-bit quantization when loading the model
chatbot = pipeline(
    "text-generation",
    model="meta-llama/Llama-3.1-8B-Instruct",
    model_kwargs={"quantization_config": quantization_config},
    torch_dtype=torch.float16,
    device_map="auto"
)

# Adjust generation parameters to further reduce memory usage
response = chatbot(
    messages,
    max_new_tokens=512,  # Adjust based on your needs
    do_sample=True,
    temperature=0.7,
    top_p=0.9,
)
for response_rol in response[0]["generated_text"]:
    if response_rol["role"] == "assistant":
        print(response_rol["content"])