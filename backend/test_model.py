# test_model.py
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from peft import PeftModel

# 1) Ścieżka do folderu z Twoimi wytrenowanymi adapterami LoRA
ADAPTER_DIR = "luna-lora"

# 2) Bazowy model, na którym trenowałeś
BASE_MODEL = "gpt2"

# 3) Ładujemy tokenizer i bazowy model
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
base_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    load_in_8bit=True,      # wymaga bitsandbytes
    device_map="auto"
)

# 4) Nakładamy adapter LoRA
model = PeftModel.from_pretrained(base_model, ADAPTER_DIR, torch_dtype=torch.float16)

# 5) Tworzymy pipeline
generator = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    device=0                # GPU; jeśli CPU → device=-1
)

# 6) Testowy prompt
prompt = "User: Hi Luna, tell me a flirty joke.\nAI:"
out = generator(prompt, max_new_tokens=50, temperature=0.8)

# 7) Wyświetlamy samą odpowiedź
reply = out[0]["generated_text"].split("AI:")[-1].strip()
print("AI reply:", reply)
