from transformers import pipeline, BitsAndBytesConfig
import torch

# Configure 4-bit quantization
quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_use_double_quant=True
)

system_file = "tests/data/system.txt"

with open(system_file, "r") as file:
    system_content = file.read()

user_file = "tests/data/user.txt"
with open(user_file, "r") as file:
    user_content = file.read()

user_content += "\nEl relato debe tener entre 2500 y 3000 palabras"

messages = [
    {"role": "system", "content": system_content},
    {"role": "user", "content": user_content},
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

output_file = "target/output.txt"

content = ""
for response_rol in response[0]["generated_text"]:
    if response_rol["role"] == "assistant":
        content = response_rol["content"]

with open(output_file, 'w') as f:
    f.write(content)

print(f"Output written to {output_file}")
print(f"Word count: {len(content.split())}")