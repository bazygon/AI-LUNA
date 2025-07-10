# backend/train_lora_fast.py

from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
    Trainer,
    TrainingArguments
)
from peft import LoraConfig, get_peft_model
import torch

def main():
    # 1) Wczytanie danych z JSONL – bez parametru jsonlines
    ds = load_dataset(
        "json",
        data_files={"train": "data/train.jsonl", "validation": "data/valid.jsonl"},
        split="train"               # wczytujemy tylko split 'train'
    )

    # 2) Tokenizer
    tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-small")
    tokenizer.pad_token = tokenizer.eos_token

    def tokenize_fn(batch):
        in_enc  = tokenizer(batch["prompt"],      truncation=True, padding="max_length", max_length=128)
        out_enc = tokenizer(batch["completion"], truncation=True, padding="max_length", max_length=128)
        in_enc["labels"] = out_enc["input_ids"]
        return in_enc

    tokenized = ds.map(tokenize_fn, batched=True, remove_columns=["prompt", "completion"])

    # 3) QLoRA 4-bit
    bnb = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4"
    )
    base = AutoModelForCausalLM.from_pretrained(
        "microsoft/DialoGPT-small",
        quantization_config=bnb,
        device_map="auto"
    )

    # 4) LoRA
    peft_cfg = LoraConfig(
        r=8,
        lora_alpha=32,
        target_modules=["c_attn", "c_proj"],
        lora_dropout=0.1,
        bias="none",
        task_type="CAUSAL_LM"
    )
    model = get_peft_model(base, peft_cfg)
    model.gradient_checkpointing_enable()

    # 5) TrainingArguments
    training_args = TrainingArguments(
        output_dir="lora-adapter",
        num_train_epochs=3,
        per_device_train_batch_size=16,
        gradient_accumulation_steps=2,
        learning_rate=3e-4,
        logging_steps=100,
        save_steps=500,
        save_total_limit=2,
        fp16=True,
        push_to_hub=False
    )

    # 6) Trainer + trening
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized,
        tokenizer=tokenizer
    )
    trainer.train()

    # 7) Zapis adaptera + tokenizera
    model.save_pretrained("lora-adapter")
    tokenizer.save_pretrained("lora-adapter")
    print("✅ Trening ukończony. Adapter jest w backend/lora-adapter/")

if __name__ == "__main__":
    main()
