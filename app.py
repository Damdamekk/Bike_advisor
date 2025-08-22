import os
import json
import requests
import pickle
import pandas as pd
from flask import Flask, request, render_template

app = Flask(__name__)

# Wczytanie listy rowerów z pliku JSON
try:
    with open('wyniki.json', 'r', encoding='utf-8') as f:
        BIKES = json.load(f)
except (FileNotFoundError, json.JSONDecodeError) as e:
    BIKES = []
    print(f"Błąd wczytywania pliku JSON: {e}")

# Wczytanie modelu ML
try:
    with open("model.pkl", "rb") as f:
        model, encoders = pickle.load(f)
except Exception as e:
    model, encoders = None, None
    print(f"Błąd wczytywania modelu: {e}")

# Konfiguracja Ollamy
OLLAMA_HOSTNAME = os.environ.get("OLLAMA_HOSTNAME", "127.0.0.1")
OLLAMA_PORT = os.environ.get("OLLAMA_PORT", "11434")

def query_ollama(prompt: str) -> str:
    try:
        url = f"http://{OLLAMA_HOSTNAME}:{OLLAMA_PORT}/api/generate"
        response = requests.post(url, json={"model": "mistral", "prompt": prompt}, stream=True)
        response.raise_for_status()

        full_response = ""
        for line in response.iter_lines():
            if line:
                data = json.loads(line.decode('utf-8'))
                full_response += data.get("response", "")
                if data.get("done", False):
                    break
        return full_response.strip()
    except Exception as e:
        return f"Błąd przy próbie połączenia z Ollama: {e}"

def predict_top3_bikes_ml(user_input, bikes_json):
    X = pd.DataFrame([user_input])
    for col in X.columns:
        if col in encoders:
            if user_input[col] not in encoders[col].classes_:
                X[col] = encoders[col].transform([encoders[col].classes_[0]])
            else:
                X[col] = encoders[col].transform([user_input[col]])

    proba = model.predict_proba(X)[0]
    top3_idx = proba.argsort()[::-1]  # posortowane od najwyższego

    # Konwersja predykcji do nazw
    top3_labels = model.classes_[top3_idx]
    top3_names = encoders["rower"].inverse_transform(top3_labels)

    unique_bikes = []
    seen = set()
    for name in top3_names:
        if name not in seen:
            match = next((b for b in bikes_json if b["Nazwa"] == name), None)
            if match:
                unique_bikes.append(match)
                seen.add(name)
        if len(unique_bikes) == 3:
            break
    return unique_bikes

def format_response_llm(komentarz, wybrane_rowery):
    html = "<h3>Propozycje i uzasadnienia</h3><ul>"
    for i, bike in enumerate(wybrane_rowery):
        czesc = ""
        try:
            czesc = komentarz.split(f"{i+1}.")[1].split(f"{i+2}.")[0].strip()
        except:
            czesc = komentarz.strip()
        html += f"<li><b>{bike['Nazwa']}</b> – <a href='{bike['Link']}' target='_blank'>{bike['Link']}</a><br><p>{czesc}</p></li>"
    html += "</ul>"
    return html

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user = request.form.get('uzytkownik')
        budget = request.form.get('budzet')
        purpose = request.form.get('cel')
        frequency = request.form.get('czestotliwosc')
        terrain = request.form.get('teren')
        experience = request.form.get('doswiadczenie')
        weather = request.form.get('pogoda')
        distance = request.form.get('dystans')

        try:
            numeric_budget = float(budget)
            numeric_distance = float(distance)
        except ValueError:
            return render_template('form.html', wynik="Nieprawidłowe dane liczbowe.")

        user_input = {
            "uzytkownik": user.lower(),
            "budzet": numeric_budget,
            "cel": purpose.lower(),
            "czestotliwosc": frequency.lower(),
            "teren": terrain.lower(),
            "doswiadczenie": experience.lower(),
            "pogoda": weather.lower(),
            "dystans": numeric_distance
        }

        if not model or not encoders:
            return render_template('form.html', wynik="Model nie jest załadowany.")

        wybrane_rowery = predict_top3_bikes_ml(user_input, BIKES)

        bike_list = ""
        for i, rower in enumerate(wybrane_rowery, 1):
            bike_list += f"{i}. {rower['Nazwa']} – {rower['Link']}\n"

        prompt = f"""
Jesteś doradcą rowerowym. Użytkownik opisał swoje potrzeby, a poniżej znajduje się lista trzech wybranych rowerów.
Napisz OSOBNY komentarz (2-3 zdania) do każdego z nich – wyjaśnij, dlaczego dany rower pasuje do użytkownika.

Informacje o użytkowniku:
- Kto użytkuje: {user}
- Budżet: {budget} PLN
- Cel użytkowania: {purpose}
- Częstotliwość jazdy: {frequency}
- Teren jazdy: {terrain}
- Doświadczenie: {experience}
- Warunki pogodowe: {weather}
- Typowy dystans: {distance} km

Wybrane rowery:
{bike_list}

Użyj języka POLSKIEGO.
"""

        response_text = query_ollama(prompt)
        response_html = format_response_llm(response_text, wybrane_rowery)
        return render_template('form.html', wynik=response_html)

    return render_template('form.html', wynik=None)

if __name__ == '__main__':
    app.run(debug=True)
