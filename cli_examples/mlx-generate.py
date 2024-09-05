#!/usr/bin/env python3

# Use mlx libraries
# Examples are tested on Macbook with M (arm64) chip

# ------------------------
# Load necessary libraries
import mlx_lm
from mlx_lm import load, generate

# -------------------------
# specify model names
model_id = "mlx-community/gemma-2-9b-it-4bit"   # This has to be a 'converted' mlx model
# examples are:
# meta llama3: mlx-community/Meta-Llama-3-8B-Instruct-4bit
# apple openELM: mlx-community/OpenELM-1_1B-Instruct-4bit
# microsoft phi3: mlx-community/Phi-3-mini-128k-instruct-4bit
# google gemma2: mlx-community/gemma-2-9b-it-4bit
# 

# assign to anything other than None, if an adaptor is wanted. This
# can be an adaptor from LORA training.
adaptor_id = None


# -------------------------
# Extra config for model
model_config = {}

# -------------------------
# Extra config for tokenizer
#tokenizer_config = {}
#tokenizer_config = {"trust_remote_code": True}
#tokenizer_config = {"eos_token": "<|end|>"}   # this is for Phi-3
#tokenizer_config = {"eos_token": "<|eot_id|>", "trust_remote_code": True} # this is for Llama3
tokenizer_config = {"eos_token": "<end_of_turn>", "trust_remote_code": True} # this is for Gemma2


# -------------------------
# load model

t_model, t_tokenizer = load( model_id, adapter_path = adaptor_id, model_config = model_config, tokenizer_config = tokenizer_config )

# -------------------------
# some testing messages
input_messages = [
    """Title: Gene expression profile at single cell level of bone marrow cells in 5TGM1 multiple myeloma mouse model treated with CD24 CAR-T cells
Summary: Durable remissions following anti-B cell maturation antigen (BCMA)-specific chimeric antigen receptor (CAR) T-cell treatment of multiple myeloma (MM) are rare. Relapses occur when a small subset of MM tumor-initiating cells (TICs) survive treatment. MM cells expressing CD24 exhibit features of TICs. We developed CD24-CAR-T cells and tested their ability to eliminate MM TICs in vitro and in vivo.
Overall design: We analyzed the immune cell changes in the BM microenvironment of the 5TGM1 mouse model treated with CD24 CAR-T cells using single-cell RNA sequencing (scRNA-seq).
Question: What is the data type?
""",
   """Title: Expression data of plasma cell from MGUS patients
Summary: Multiple myeloma is preceded by monoclonal gammopathy of undetermined significance (MGUS). Serum markers are currently used to stratify MGUS patients into clinical risk groups. A molecular signature predicting MGUS progression has not been produced. We have explored the use of gene expression profiling to risk-stratify MGUS and developed an optimized signature based on large samples with long-term follow-up. Microarray analysis of mRNA from MGUS patients with stable disease and MGUS patients that progressed to MM within 10 years, was used to define a molecular signature of MGUS risk.
Overall design: Bone marrow plasma cells from MGUS patients were enriched by anti-CD138 immunomagnetic beads for RNA extraction and hybridization on Affymetrix microarrays. We sought to identify genetic differences in the bone marrow plasma cells of stable and progressive MGUS patients. Patients who progressed to MM within 10 years after diagnosis of MGUS were considered Progressing (P), while the other 334 MGUS had not progressed called Stable (S).
Question: What is the data type?
""",
   """Title: Effect of NEK2 deficiency on gene expression of CD19-selected spleen B cells of Eµ-myc mouse model
Summary: NEK2 overexpression in the B cell lineage affects B cell development. To determine whether deficiency of NEK2 inhibits B cell malignancies, we crossed Nek2 knockout mice with Eµ-myc transgenic mice, a well-established Myc-driven preclinical model for B cell malignancies. Three genotyping offsprings were obtained: Eµ-myc/Nek2+/+ (NEK2 wild type), Eµ-myc/Nek2+/- (NEK2 heterozygotes), and Eµ-myc/Nek2-/- (NEK2 homozygotes). Bulk RNA-seq was performed on CD19-selected spleen B cells to view the transcriptome differences.
Overall design: Comparative gene expression profiling analysis of RNA-seq data for CD19-selected spleen B cells from 6-8 weeks old Eµ-myc mice with indicated NEK2 deficiency.
Question: What is the data type?
"""]

# -------------------------
# generate output
for i, msg in enumerate(input_messages):
    if hasattr(t_tokenizer, "apply_chat_template") and t_tokenizer.chat_template:
        prompt = t_tokenizer.apply_chat_template([{'role': 'user', 'content': msg}], tokenize=False, add_generation_prompt=True) #apply chat template
        response = generate(t_model, t_tokenizer, prompt=prompt, temp=0.1, verbose=False)
        #print(response)
        # we will add the first conversation to the next prompt (perhaps
        # one conversation is enough, but I want to show how conversation
        # history/memory works
        second_prompt = t_tokenizer.apply_chat_template([{'role': 'user', 'content': msg},{'role': 'assistant', 'content': response},{'role': 'user', 'content': "Then, summarize one word for the data type. For example, \"RNA-seq\", \"scRNA-seq\", \"ChIP-seq\", \"ATAC-seq\", or \"Microarray\"."}], tokenize=False, add_generation_prompt=True)
        final_response = generate(t_model, t_tokenizer, prompt=second_prompt, temp=0.1, verbose=False)
    else:
        # if there is no chat_template
        final_response = generate(t_model, t_tokenizer, prompt=msg, temp=0.1, verbose=False)
    
    print ( i+1, ":", final_response )
