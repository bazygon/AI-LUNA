# prepare_data.py
import os
import json
import random
from datasets import load_dataset

# 1) Źródła dialogów
SOURCES = [
    ("bavard/personachat_truecased", {"split": "train", "trust_remote_code": True}),
    ("daily_dialog",               {"split": "train", "trust_remote_code": True}),
    ("facebook/empathetic_dialogues", {"split": "train"}),
    ("blended_skill_talk",         {"split": "train"}),
]

def extract_pairs(example):
    """
    Zwraca listę {"prompt":..., "completion":...} dla pojedynczego przykładu.
    Obsługuje cztery schematy danych:
      - persona-chat truecased (pola "prompt" i "utterance")
      - daily_dialog    (pole "dialog": lista stringów)
      - empathetic_dialogues (pole "dialogue": lista dictów {"utterance":...})
      - blended_skill_talk   (pole "utterances": lista stringów)
    """
    # --- PersonaChat truecased
    if "prompt" in example and "utterance" in example:
        return [{
            "prompt": example["prompt"] + "\nAI:",
            "completion": " " + example["utterance"]
        }]

    # --- pozostałe: ustalamy listę kolejnych wypowiedzi
    if "dialog" in example:
        dialogs = example["dialog"]
    elif "dialogue" in example:
        dialogs = [turn["utterance"] for turn in example["dialogue"]]
    elif "utterances" in example:
        dialogs = example["utterances"]
    else:
        return []

    pairs = []
    for i in range(len(dialogs) - 1):
        p = f"User: {dialogs[i]}\nAI:"
        c = " " + dialogs[i + 1]
        pairs.append({"prompt": p, "completion": c})
    return pairs

def main():
    all_pairs = []
    for repo_id, cfg in SOURCES:
        print(f"🔄 Ładuję {repo_id} …")
        ds = load_dataset(repo_id, **cfg)
        for ex in ds:
            all_pairs.extend(extract_pairs(ex))

    print(f"✅ Wygenerowano łącznie {len(all_pairs)} par. Mieszam …")
    random.seed(42)
    random.shuffle(all_pairs)

    split_at = int(0.8 * len(all_pairs))
    os.makedirs("data", exist_ok=True)
    with open("data/train.jsonl", "w", encoding="utf-8") as ftr, \
         open("data/valid.jsonl", "w", encoding="utf-8") as fval:
        for idx, pair in enumerate(all_pairs):
            line = json.dumps(pair, ensure_ascii=False)
            if idx < split_at:
                ftr.write(line + "\n")
            else:
                fval.write(line + "\n")

    print(f"✅ Zapisano {split_at} rekordów do data/train.jsonl i {len(all_pairs)-split_at} do data/valid.jsonl")

if __name__ == "__main__":
    main()
