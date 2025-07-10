# backend/merge_lora.py
import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

BASE_MODEL  = "gpt2"
ADAPTER_DIR = os.path.join(os.path.dirname(__file__), "luna-lora")
MERGED_DIR  = os.path.join(os.path.dirname(__file__), "luna-merged")

# 1) Tokenizer bazowy
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)

# 2) Bazowy model
if torch.cuda.is_available():
    base = AutoModelForCausalLM.from_pretrained(BASE_MODEL, torch_dtype=torch.float16).to("cuda")
else:
    base = AutoModelForCausalLM.from_pretrained(BASE_MODEL)

# 3) Załaduj adapter LoRA
model = PeftModel.from_pretrained(
    base,
    ADAPTER_DIR,
    torch_dtype=torch.float16 if torch.cuda.is_available() else None
)

# 4) Zmerguj adapter
merged = model.merge_and_unload()

# 5) Zapisz zmergowany model + tokenizer
os.makedirs(MERGED_DIR, exist_ok=True)
merged.save_pretrained(MERGED_DIR)
tokenizer.save_pretrained(MERGED_DIR)

print(f">>> Zmergowany model zapisany w: {MERGED_DIR}")
