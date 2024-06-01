#!/usr/bin/env python3

# Using Huggingface libraries
# Examples are tested on Macbook with M (arm64) chip

# ------------------------
# Load necessary libraries
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

torch.random.manual_seed(0)

device = "mps"

# -------------------------
# specify model names
model_id = "microsoft/biogpt"
tokenizer_id = "microsoft/biogpt"
peft_model_id = None

# -------------------------
# load model
model = AutoModelForCausalLM.from_pretrained(
        model_id,
        device_map=device,
        torch_dtype="auto",
        trust_remote_code=True,
    )

# and adaptor
if peft_model_id:                         #not None
    model.load_adapter(peft_model_id)

# -------------------------
# load tokenizer
tokenizer = AutoTokenizer.from_pretrained(tokenizer_id)

# -------------------------
# make a message with common chat msg format
messages = [
    {"role": "user",
     "content": """
Title: Single cell RNA sequencing of primary breast cancer.
Summary: We performed single cell RNA sequencing (RNA-seq) for 549 primary breast cancer cells and lymph node metastases from 11 patients with distinct molecular subtypes (BC01-BC02, estrogen receptor positive (ER+); BC03, double positive (ER+ and HER2+); BC03LN, lymph node metastasis of BC03; BC04-BC06, human epidermal growth factor receptor 2 positive (HER2+); BC07-BC11, triple-negative breast cancer (TNBC); BC07LN, lymph node metastasis of BC07) and matched bulk tumors. We separated these single cells into epithelial tumor and tumor-infiltrating immune cells using inferred CNVs from RNA-seq. The refined single cell profiles for the tumor and immune cells provide key expression signatures of breast cancer and the surrounding microenvironment.
Overall design: All single-cell mRNA expression profiles were acquired from eleven patients (BC01-BC11) including two lymph node metastases (BC03LN, BC07LN) (549 samples). We applied four filtering criteria so as to remove samples with low sequencing quality and finally obtained 515 single cell sequencing data. Matched bulk tumor tissues and/or pooled cells were also sequenced and analyzed by the single cell RNA-seq pipeline (14 samples). Bulk tumor transcriptomes showed significant correlations with the average of single cell transcriptomes.
Question: What is the data type?
"""}
]

# -------------------------
# create a pipeline for text-generation
pipe = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
    )

# set generation arguments
generation_args = {
        "max_new_tokens": 512,
        "return_full_text": False,
        "temperature": 0.1,
        "do_sample": True,
    }

# -------------------------
# generate output
output = pipe(messages, **generation_args)
print(output[0]['generated_text'])
