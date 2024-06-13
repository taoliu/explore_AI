# Instruction

Use `mlx_lm` library to set up a mini web-based chatbot on Mac
computer with M chip.

## Dependencies

```
pip install mlx-lm "huggingface-hub[cli]" accelerate flask flask-session torch transformers
```

You also need to create a huggingface account and create an "Access
Token" -- this is for downloading the model from huggingface. 

After you create the token, in the command line:

```
huggingface-cli login
```

## Steps

### 1. Run `mlx_lm.server` 

Run 

```bash
mlx_lm.server --model mlx-community/mlx-community/Meta-Llama-3-8B-Instruct-4bit

```

We will use a specific Llama3 8B model for long context length for
this chatbot.

If you have an adaptor, do this (supposing the adaptor is in the
directory of "lora_adaptor_llama3"):

```bash
mlx_lm.server --adapter-path lora_adaptor_llama3 --model mlx-community/mlx-community/Meta-Llama-3-8B-Instruct-4bit
```

The server will be running and accessible at http://localhost:8080 .
   
### 2. Run the Flask application

Run `python app.py`. The web interface can be  accessible at
http://127.0.0.1:5000/.

### 3. Use the interface

Enter the instruction input and click "Generate". Please note, the
history will be 'memorized' by being reused as input for communicating
with the LLM.

Click the "Reset" button to clear the conversation history. Or click
the "Save" button to download the conversation history as a plain text
file.
