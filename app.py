from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)
DATA_FILE = "survey_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"english": {"ChatGPT": 0, "Claude": 0, "Gemini": 0, "Copilot": 0}, "math": {"ChatGPT": 0, "Claude": 0, "Gemini": 0, "Copilot": 0}, "science": {"ChatGPT": 0, "Claude": 0, "Gemini": 0, "Copilot": 0}, "cs": {"ChatGPT": 0, "Claude": 0, "Gemini": 0, "Copilot": 0}, "history": {"ChatGPT": 0, "Claude": 0, "Gemini": 0, "Copilot": 0}, "useAI": {"Yes": 0, "No": 0}, "frqs": []}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

@app.route("/api/survey", methods=["GET"])
def get_survey_data():
    return jsonify(load_data()), 200

@app.route("/api/survey", methods=["POST"])
def submit_survey():
    form_data = request.json
    data = load_data()
    data["english"][form_data["english"]] += 1
    data["math"][form_data["math"]] += 1
    data["science"][form_data["science"]] += 1
    data["cs"][form_data["cs"]] += 1
    data["history"][form_data["history"]] += 1
    data["useAI"][form_data["useAI"]] += 1
    data["frqs"].insert(0, {"text": form_data["frq"], "timestamp": datetime.now().isoformat()})
    save_data(data)
    return jsonify({"message": "Survey submitted successfully", "data": data}), 200

if __name__ == "__main__":
    app.run(debug=True, port=5001)
