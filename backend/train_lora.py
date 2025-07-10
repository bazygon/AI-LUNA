# backend/train_lora.py

import os
import torch
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
    Trainer,
    TrainingArguments
)
from peft import LoraConfig, get_peft_model

def main():
    # 1) Ścieżki do plików JSONL
    train_file = os.path.join("data", "train_full.jsonl")
    valid_file = os.path.join("data", "valid_full.jsonl")

    # Sprawdź, czy pliki istnieją
    if not os.path.isfile(train_file):
        raise FileNotFoundError(f"Brak pliku treningowego: {train_file}")
    if not os.path.isfile(valid_file):
        raise FileNotFoundError(f"Brak pliku walidacyjnego: {valid_file}")

    # 2) Wczytaj JSONL
    ds = load_dataset(
        "json",
        data_files={"train": train_file, "validation": valid_file}
    )

    # 3) Tokenizer
    tokenizer = AutoTokenizer.from_pretrained("microsoft/DialoGPT-small")
    tokenizer.pad_token = tokenizer.eos_token

    # 4) Funkcja tokenizacji
    def tokenize_fn(batch):
        enc = tokenizer(
            batch["prompt"],
            truncation=True,
            padding="max_length",
            max_length=128
        )
        out = tokenizer(
            batch["completion"],
            truncation=True,
            padding="max_length",
            max_length=128
        )
        enc["labels"] = out["input_ids"]
        return enc

    # 5) Tokenizuj zestawy
    tokenized_train = ds["train"].map(
        tokenize_fn, batched=True, remove_columns=["prompt", "completion"]
    )
    tokenized_valid = ds["validation"].map(
        tokenize_fn, batched=True, remove_columns=["prompt", "completion"]
    )

    # 6) QLoRA 4-bit config
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4"
    )
    base_model = AutoModelForCausalLM.from_pretrained(
        "microsoft/DialoGPT-small",
        quantization_config=bnb_config,
        device_map="auto"
    )

    # 7) LoRA config
    lora_cfg = LoraConfig(
        r=8,
        lora_alpha=32,
        target_modules=["c_attn", "c_proj"],
        lora_dropout=0.1,
        bias="none",
        task_type="CAUSAL_LM"
    )
    model = get_peft_model(base_model, lora_cfg)
    model.gradient_checkpointing_enable()

    # 8) TrainingArguments
    training_args = TrainingArguments(
        output_dir="lora-adapter",
        num_train_epochs=3,
        per_device_train_batch_size=16,
        gradient_accumulation_steps=2,
        learning_rate=3e-4,
        logging_steps=100,
        evaluation_strategy="steps",
        eval_steps=200,
        save_steps=200,
        save_total_limit=2,
        fp16=True,
        push_to_hub=False
    )

    # 9) Trainer + training
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_train,
        eval_dataset=tokenized_valid,
        tokenizer=tokenizer
    )
    trainer.train()

    # 10) Zapis adaptera i tokenizera
    os.makedirs("lora-adapter", exist_ok=True)
    model.save_pretrained("lora-adapter")
    tokenizer.save_pretrained("lora-adapter")
    print("✅ Adapter wytrenowany i zapisany w backend/lora-adapter/")

if __name__ == "__main__":
    main()
