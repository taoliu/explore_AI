# Instruction

Use the `mlx_lm` library to set up a mini web-based chatbot on a Mac
computer with an M chip.

## Dependencies

First, create a conda environment:

```
conda create -n mlxAI python=3.12
conda activate mlxAI
```

or create a Python virtual environment:

```
python -m venv mlxAI
./mlxAI/bin/activate
```

Then install the following packages:

```
pip install mlx-lm "huggingface-hub[cli]" accelerate flask flask-session torch transformers
```

You also need to create a Huggingface account and create an "Access
Token" to download the model from Huggingface.

After creating the token, run the following command in the command
line:

```
huggingface-cli login
```

## Steps

### 1. Run `mlx_lm.server` 

Run the following command:

```bash
mlx_lm.server --model mlx-community/Meta-Llama-3.1-8B-Instruct-4bit

```

We only tested the Llama3 8B IT version. For other LMs, you may need
to modify `static/script.js`.

If you have an adapter, run the following command (supposing the
adapter is in the directory "lora_adaptor_llama3"):

```bash
mlx_lm.server --adapter-path lora_adaptor_llama3 --model mlx-community/Meta-Llama-3.1-8B-Instruct-4bit
```

The server API will be running and accessible at
http://127.0.0.1:8080.

### 2. Run the Flask application

Run python app.py. The web interface can be accessed at
http://127.0.0.1:5000.


### 3. Use the interface

Enter the instruction input and click "Generate". Note that the
history will be memorized and reused as input for communicating with
the LLM.

Use the "New session" button to create a new chat session. Use the
"Rename session" button to rename it. Click the "Reset session" button
to clear the conversation history. Click the "Save session" button to
download the conversation history as a plain text file. Use the
"Delete session" button to remove the chat session. All chat sessions
are saved on your own computer.

### Demo

![Demo screenshot](./demo.png?raw=true "Demo site")
