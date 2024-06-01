#!/usr/bin/env python3

# Use mlx libraries
# Examples are tested on Macbook with M (arm64) chip

# ------------------------
# Load necessary libraries
import torch
from datasets import load_dataset
from mlx_lm import load, generate, tuner


# -------------------------
# specify model names

# The model that you want to train from the Hugging Face hub
model_id = "meta-llama/Meta-Llama-3-8B-Instruct"
# Fine-tuned model name
trained_model_id = "Meta-Llama-3-8B-Instruct-RetrieverApp"
output_dir = 'working/' + trained_model_id

# -------------------------
# load the model

# For 8 bit quantization ( currently not working on mac )
quantization_config8 = BitsAndBytesConfig(load_in_8bit=True, llm_int8_threshold=200.0)

# For 4 bit quantization ( currently not working on mac )
quantization_config4 = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,)

# load
model = AutoModelForCausalLM.from_pretrained(model_id,
                                             #quantization_config=quantization_config4,
                                             device_map=device)

# -------------------------
# Load the tonenizer

tokenizer = AutoTokenizer.from_pretrained(model_id, add_eos_token=True)
tokenizer.add_special_tokens({"pad_token":"<pad>"})
tokenizer.pad_token_id = tokenizer.convert_tokens_to_ids(tokenizer.pad_token)

# Set the terminators
terminators = [
    tokenizer.eos_token_id,
    tokenizer.convert_tokens_to_ids("<|eot_id|>") ]

# -------------------------
# Set training Arguments
training_args = TrainingArguments(
    output_dir=output_dir,
    evaluation_strategy="steps",
    do_eval=True,
    optim="adamw_torch",
    per_device_eval_batch_size=1, # originally set to 8
    per_device_train_batch_size=1, # originally set to 8
    gradient_accumulation_steps=4,
    log_level="info",
    save_strategy="epoch",
    logging_steps=100,
    learning_rate=1e-4,
    #fp16= not torch.cuda.is_bf16_supported(), # only for cuda
    #bf16= torch.cuda.is_bf16_supported(), # only for cuda
    eval_steps=100,
    num_train_epochs=10,
    warmup_ratio=0.1,
    lr_scheduler_type="linear",
    seed=42,
)

# LORA arguments
peft_config = LoraConfig(
    r=64, # LoRA attention dimension
    lora_alpha=16, # Alpha parameter for LoRA scaling
    lora_dropout=0.1, # Dropout probability for LoRA layers
    bias="none",
    task_type="CAUSAL_LM",
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "down_proj", "up_proj"],
)

set_seed(1234)  # For reproducibility

# -------------------------
# load datasets
dataset = load_dataset("training_data")

# -------------------------
# Training
trainer = SFTTrainer(
    model=model,
    args=training_args,
    train_dataset=dataset['train'],
    eval_dataset=dataset['validation'],
    peft_config=peft_config,
    tokenizer=tokenizer,
    packing=True,
    max_seq_length=500,
)

# To clear out cache for unsuccessful run
torch.mps.empty_cache()

# train
trainer.train()

# save model in local
trainer.save_model()
