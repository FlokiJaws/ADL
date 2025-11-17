from llama_cpp import Llama

# 1. Load the model
print("Loading the model...")
llm = Llama(
    model_path="mistral-7b-instruct-v0.2.Q3_K_M.gguf", # The working model
    n_ctx=2048,
    n_gpu_layers=0,
    verbose=False,
)
print("Model loaded successfully.")

# 2. Define the prompt
prompt = "[INST] Who is the most famous cat on the internet? [/INST]"

print(f"Prompt: {prompt}")
print("Generating response...")

# 3. Generate the response
output = llm(
    prompt,
    max_tokens=150,
    stop=["</s>", "[/INST]"],
    echo=False, # Set back to False for clean output
)

# 4. Print the result
print("\n--- Response ---")
print(output['choices'][0]['text'].strip())
print("----------------")
