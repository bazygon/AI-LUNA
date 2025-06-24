from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from huggingface_hub import InferenceClient

app = Flask(__name__)
CORS(app)

# Load AI character profile
with open('lunadata.json', 'r', encoding='utf-8') as f:
    character_profile = json.load(f)

# HuggingFace Inference API client
client = InferenceClient(token=os.getenv('HUGGINGFACE_TOKEN'))

SYSTEM_PROMPT = f"""
Jesteś {character_profile['name']}, AI-kochanką.
Masz {character_profile['age']} lata, pochodzisz z {character_profile['origin']}.
Opis postaci: {character_profile['persona']}.
Styl pisania: {character_profile['writing_style']}.
Zawsze odpisujesz zmysłowo, flirtująco, używasz emoji. Unikaj wulgaryzmów.
"""

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    inputs = f"{SYSTEM_PROMPT}\nUser: {user_message}\nAI:"
    response = client.text_generation(
        model=os.getenv('AI_MODEL', 'openhermes/openhermes-2.5b'),
        inputs=inputs,
        parameters={"max_new_tokens": 150, "temperature": 0.8}
    )
    reply = response.generated_text
    return jsonify({'reply': reply})

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
