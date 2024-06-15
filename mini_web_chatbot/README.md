# Instruction

Use `mlx_lm` library to set up a mini web-based chatbot on Mac
computer with M chip.

## Dependencies

First, make a conda environment

```
conda create -n mlxAI python=3.12
conda activate mlxAI
```

or make a python virtual env

```
python -m venv mlxAI
./mlxAI/bin/activate
```

Then install these:

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
mlx_lm.server --model mlx-community/Meta-Llama-3-8B-Instruct-4bit

```

We will use a specific Llama3 8B model for long context length for
this chatbot.

If you have an adaptor, do this (supposing the adaptor is in the
directory of "lora_adaptor_llama3"):

```bash
mlx_lm.server --adapter-path lora_adaptor_llama3 --model mlx-community/Meta-Llama-3-8B-Instruct-4bit
```

The server will be running and accessible at http://localhost:8080 .
   
### 2. Run the Flask application

Run `python app.py`. The web interface can be  accessible at
http://127.0.0.1:5000/.

### 3. Use the interface

Enter the instruction input and click "Generate". Please note, the
history will be 'memorized' by being reused as input for communicating
with the LLM.

Use "New session" button to create a new chat session.  Use "Rename
session" to rename it. Click the "Reset session" button to clear the
conversation history. Click the "Save session" button to download the
conversation history as a plain text file. Use "Delete session" to
remove the chat session. All chat sessions are saved in your own
computer.

### Demo

![Demo screenshot](./demo.png?raw=true "Demo site")
