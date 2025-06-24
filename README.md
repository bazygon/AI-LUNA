# AI Companion Luna - MVP

## Opis
To jest minimalna wersja MVP erotycznej aplikacji czatu z AI-towarzyszką "Luna".

## Struktura projektu
- backend/
  - app.py          # Główny serwer Flask
  - lunadata.json   # Profil AI Luny
  - .env.example    # Przykładowe zmienne środowiskowe
  - requirements.txt
- frontend/
  - index.html
  - main.js
  - style.css
- README.md

## Wymagania
- Python 3.9+
- Konto HuggingFace z tokenem (jeśli używasz HuggingFace Inference API)

## Instalacja backendu
1. Sklonuj repozytorium.
2. Utwórz virtualenv:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate   # Windows
   ```
3. Zainstaluj zależności:
   ```bash
   pip install -r backend/requirements.txt
   ```
4. Skopiuj `.env.example` do `.env` i uzupełnij:
   ```
   HUGGINGFACE_TOKEN=twój_token
   AI_MODEL=openhermes/openhermes-2.5b
   PORT=5000
   ```
5. Uruchom backend:
   ```bash
   cd backend
   flask run --host=0.0.0.0 --port 5000
   ```

## Uruchomienie frontendu
1. Otwórz `frontend/index.html` w przeglądarce lub hostuj na Netlify/Vercel.
2. Zmień URL w `frontend/main.js` na adres Twojego serwera.

## Rozszerzenia
- Integracja płatności (Gumroad, Boosty.to).
- Generowanie obrazów AI (Stable Diffusion).
- Głos AI (Bark, Tortoise TTS).
