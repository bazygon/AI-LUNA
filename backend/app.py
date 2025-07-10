import os, json, torch
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

# 1) Flask + CORS + frontend
app = Flask(__name__, static_folder="../frontend", static_url_path="")
CORS(app, origins="*")

# 2) Profil postaci
with open(os.path.join(os.path.dirname(__file__), "lunadata.json"), encoding="utf-8") as f:
    profile = json.load(f)
BOT_NAME = profile["name"]

# 3) Załaduj tokenizer + model + adapter LoRA
ADAPTER_DIR = "lora-adapter"
BASE_MODEL  = "microsoft/DialoGPT-small"

tokenizer = AutoTokenizer.from_pretrained(ADAPTER_DIR, local_files_only=True)
tokenizer.pad_token = tokenizer.eos_token

base = AutoModelForCausalLM.from_pretrained(BASE_MODEL, local_files_only=True)
model = PeftModel.from_pretrained(base, ADAPTER_DIR, local_files_only=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
if torch.cuda.is_available():
    model.half()
model.eval()

# 4) Serwowanie strony
@app.route("/", methods=["GET"])
def index():
    return send_from_directory(app.static_folder, "index.html")

# 5) Endpoint czatu
@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)
    user_msg = data.get("message", "").strip()
    if not user_msg:
        return jsonify(error="No message"), 400

    # --- LOG user input ---
    print(f"\n💬 You: '{user_msg}'")

    # Budujemy prompt
    prompt = (
        f"You are {BOT_NAME}, a sensual AI companion.\n"
        f"Persona: {profile['persona']}. Style: {profile['writing_style']}.\n\n"
        f"You: {user_msg}\n{BOT_NAME}:"
    )

    # Tokenizacja
    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=128,
        padding="max_length"
    ).to(device)

    # Generacja odpowiedzi
    out = model.generate(
        **inputs,
        max_new_tokens=100,
        min_new_tokens=5,
        do_sample=True,
        temperature=0.8,
        top_p=0.9,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=tokenizer.eos_token_id,
        no_repeat_ngram_size=2
    )

    # Wyciągamy tylko nowe tokeny
    gen = out[0, inputs.input_ids.shape[-1]:]
    raw_reply = tokenizer.decode(gen, skip_special_tokens=True).strip()
    reply = f"{BOT_NAME}: {raw_reply}"

    # --- LOG bot reply ---
    print(f"💻 {reply!r}\n")

    return jsonify(reply=reply)

# 6) Start serwera
if __name__=="__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"🚀 Server running on http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port)
