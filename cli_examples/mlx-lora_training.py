#!/usr/bin/env python3

# Use mlx libraries
# Examples are tested on Macbook with M (arm64) chip

# ------------------------
# Load necessary libraries
import math
import re
import types
from pathlib import Path

import mlx.nn as nn
import mlx.optimizers as optim
import numpy as np
import yaml
from mlx.utils import tree_flatten

from mlx_lm.tuner.datasets import load_dataset
from mlx_lm.tuner.trainer import TrainingArgs, TrainingCallback, evaluate, train
from mlx_lm.tuner.utils import apply_lora_layers, build_schedule, linear_to_lora_layers
from mlx_lm.utils import load, save_config


# -------------------------
# training configuration
TR_CONFIG = {
    "model": "mlx-community/Meta-Llama-3-8B-Instruct-4bit", # The path to the local model directory or Hugging Face repo.
    "data": "training_data/",             # Directory with {train, valid, test}.jsonl files
    "seed": 0,                            # The PRNG seed
    "lora_layers": 16,                    # Number of layers to fine-tune
    "batch_size": 8,                      # Minibatch size.
    "iters": 100,                         # Iterations to train for.
    "val_batches": -1,                    # Number of validation batches, -1 uses the entire validation set.
    "learning_rate": 1e-5,                # Adam learning rate.
    "steps_per_report": 10,               # Number of training steps between loss reporting.
    "steps_per_eval": 10,                 # Number of training steps between validations.
    "adapter_path": "working/llama3-adaptor",   # Save/load path for the trained adapter weights.
    "save_every": 100,                          # Save the model every N iterations.
    "test_batches": -1,                         # Number of test set batches, -1 uses the entire test set.
    "max_seq_length": 1024,               # Maximum sequence length.
    "lr_schedule":{},
    #"lr_schedule": {                      # Schedule, it will overite learning_rate, uncomment and replace to use
    #    "name": "cosine_decay",
    #    "warmup": 100,                    # 0 for no warmup"
    #    "warmup_init": 1e-7,              # 0 if not specified
    #    "arguments": [1e-5, 1000, 1e-7]   # passed to scheduler
    #    },
    "lora_parameters": {                  # LoRA parameters can only be specified in a config file
        "keys": [   # The layer keys to apply LoRA to. These will be applied for the last lora_layers
                  "self_attn.q_proj",     # Here we list all Linear Layers in Llama
                  "self_attn.k_proj",
                  "self_attn.v_proj",
                  "self_attn.o_proj",
                  "self_attn.gate_proj",
                  "self_attn.down_proj",
                  "self_attn.up_proj",
                ],
        "rank": 8,
        "alpha": 16,
        "dropout": 0.0,
        "scale": 10.0
        },
    "use_dora": False,                    # Use DoRA instead of LoRA.
    "train": True, # keep it True!
    "test": True,  # keep it True!
}

# convert into args
args = types.SimpleNamespace(**TR_CONFIG)

# -------------------------
# Extra config for model
model_config = {}

# -------------------------
# Extra config for tokenizer
#tokenizer_config = {}
#tokenizer_config = {"trust_remote_code": True}
#tokenizer_config = {"eos_token": "<|end|>"}   # this is for Phi-3
tokenizer_config = {"eos_token": "<|eot_id|>", "trust_remote_code": True} # this is for Llama3
#tokenizer_config = {"eos_token": "<eos>", "trust_remote_code": True} # this is for Gemma

# random seed
np.random.seed(args.seed)

# -------------------------
# load model

t_model, t_tokenizer = load( args.model, model_config = model_config, tokenizer_config = tokenizer_config )

# Freeze all layers
t_model.freeze()

# -------------------------
# Load the tonenizer

adapter_path = Path(args.adapter_path)
adapter_file = adapter_path / "adapters.safetensors"

adapter_path.mkdir(parents=True, exist_ok=True)
save_config(vars(args), adapter_path / "adapter_config.json")

# Convert linear layers to lora layers and unfreeze in the process
linear_to_lora_layers(
    t_model,
    args.lora_layers,
    args.lora_parameters,
    args.use_dora )

print("Loading datasets")
train_set, valid_set, test_set = load_dataset(args, t_tokenizer)

print("Training")
# init training args
training_args = TrainingArgs(
    batch_size=args.batch_size,
    iters=args.iters,
    val_batches=args.val_batches,
    steps_per_report=args.steps_per_report,
    steps_per_eval=args.steps_per_eval,
    steps_per_save=args.save_every,
    adapter_file=adapter_file,
    max_seq_length=args.max_seq_length,
    )

t_model.train()
opt = optim.AdamW(                        #we can use Adam or AdamW or 
    learning_rate=(
        build_schedule(args.lr_schedule)
        if args.lr_schedule
        else args.learning_rate
        )
    )

# Train model
train(
        model=t_model,
        tokenizer=t_tokenizer,
        args=training_args,
        optimizer=opt,
        train_dataset=train_set,
        val_dataset=valid_set,
        training_callback=None,
    )

print("Testing")
t_model.eval()

test_loss = evaluate(
        model=t_model,
        dataset=test_set,
        tokenizer=t_tokenizer,
        batch_size=args.batch_size,
        num_batches=args.test_batches,
        max_seq_length=args.max_seq_length,
    )

test_ppl = math.exp(test_loss)

print(f"Test loss {test_loss:.3f}, Test ppl {test_ppl:.3f}.")
