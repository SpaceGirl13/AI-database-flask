# app.py - Complete Flask Backend
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

DATA_FILE = 'survey_data.json'

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    else:
        return {
            'english': {'ChatGPT': 0, 'Claude': 0, 'Gemini': 0, 'Copilot': 0},
            'math': {'ChatGPT': 0, 'Claude': 0, 'Gemini': 0, 'Copilot': 0},
            'science': {'ChatGPT': 0, 'Claude': 0, 'Gemini': 0, 'Copilot': 0},
            'cs': {'ChatGPT': 0, 'Claude': 0, 'Gemini': 0, 'Copilot': 0},
            'history': {'ChatGPT': 0, 'Claude': 0, 'Gemini': 0, 'Copilot': 0},
            'useAI': {'Yes': 0, 'No': 0},
            'frqs': []
        }

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@app.route('/')
def index():
    return render_template_string(SURVEY_HTML)

@app.route('/api/survey', methods=['GET'])
def get_survey_data():
    try:
        data = load_data()
        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/survey', methods=['POST'])
def submit_survey():
    try:
        form_data = request.json
        
        required_fields = ['english', 'math', 'science', 'cs', 'history', 'useAI', 'frq']
        for field in required_fields:
            if field not in form_data or not form_data[field]:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        data = load_data()
        
        data['english'][form_data['english']] += 1
        data['math'][form_data['math']] += 1
        data['science'][form_data['science']] += 1
        data['cs'][form_data['cs']] += 1
        data['history'][form_data['history']] += 1
        data['useAI'][form_data['useAI']] += 1
        
        frq_entry = {
            'text': form_data['frq'],
            'timestamp': datetime.now().isoformat()
        }
        data['frqs'].insert(0, frq_entry)
        
        save_data(data)
        
        return jsonify({
            'message': 'Survey submitted successfully',
            'data': data
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

SURVEY_HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>AI Usage Survey</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: #f5f5f5;
            padding: 20px;
        }
        
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 30px;
        }
        
        .question-block {
            background: #f9f9f9;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 8px;
            border-left: 4px solid #4CAF50;
        }
        
        .question-title {
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 15px;
            color: #333;
        }
        
        .option-label {
            display: flex;
            align-items: center;
            padding: 10px;
            background: white;
            border-radius: 6px;
            margin-bottom: 8px;
            cursor: pointer;
            transition: background 0.3s;
        }
        
        .option-label:hover {
            background: #e8f5e9;
        }
        
        input[type="radio"] {
            margin-right: 10px;
            cursor: pointer;
        }
        
        textarea {
            width: 100%;
            min-height: 120px;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 6px;
            font-family: inherit;
            font-size: 14px;
            resize: vertical;
        }
        
        textarea:focus {
            outline: none;
            border-color: #4CAF50;
        }
        
        button {
            background: #4CAF50;
            color: white;
            padding: 15px 40px;
            border: none;
            border-radius: 6px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            display: block;
            margin: 30px auto 0;
        }
        
        button:hover {
            background: #45a049;
        }
        
        .recent-frqs {
            background: #e3f2fd;
            padding: 20px;
            margin-bottom: 30px;
            border-radius: 8px;
            border-left: 4px solid #2196F3;
        }
        
        .recent-frqs h3 {
            color: #333;
            margin-bottom: 15px;
            font-size: 18px;
        }
        
        .frq-item {
            background: white;
            padding: 12px;
            margin-bottom: 10px;
            border-radius: 6px;
        }
        
        .frq-text {
            color: #555;
            line-height: 1.5;
            margin-bottom: 5px;
        }
        
        .frq-time {
            color: #888;
            font-size: 12px;
        }
        
        .results-section {
            display: none;
            margin-top: 40px;
        }
        
        .chart-container {
            background: white;
            padding: 20px;
            margin-bottom: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        }
        
        .chart-container h3 {
            color: #555;
            margin-bottom: 15px;
            text-align: center;
        }
        
        canvas {
            max-height: 300px;
        }
        
        #surveyForm {
            display: block;
        }
        
        #surveyForm.hidden {
            display: none;
        }
        
        .success-message {
            background: #4CAF50;
            color: white;
            padding: 15px;
            border-radius: 6px;
            text-align: center;
            margin-bottom: 20px;
            display: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>AI Usage Survey</h1>
        
        <div class="success-message" id="successMessage">
            ✓ Thank you! Your response has been submitted. Scroll down to see the results!
        </div>
        
        <div id="recentFRQs"></div>
        
        <div id="surveyForm">
            <div class="question-block">
                <div class="question-title">1. What AI source do you find the most useful for English work?</div>
                <label class="option-label"><input type="radio" name="english" value="ChatGPT" required> ChatGPT</label>
                <label class="option-label"><input type="radio" name="english" value="Claude"> Claude</label>
                <label class="option-label"><input type="radio" name="english" value="Gemini"> Gemini</label>
                <label class="option-label"><input type="radio" name="english" value="Copilot"> Microsoft Copilot</label>
            </div>

            <div class="question-block">
                <div class="question-title">2. What AI source do you find the most useful for Math work?</div>
                <label class="option-label"><input type="radio" name="math" value="ChatGPT" required> ChatGPT</label>
                <label class="option-label"><input type="radio" name="math" value="Claude"> Claude</label>
                <label class="option-label"><input type="radio" name="math" value="Gemini"> Gemini</label>
                <label class="option-label"><input type="radio" name="math" value="Copilot"> Microsoft Copilot</label>
            </div>

            <div class="question-block">
                <div class="question-title">3. What AI source do you find the most useful for Science work?</div>
                <label class="option-label"><input type="radio" name="science" value="ChatGPT" required> ChatGPT</label>
                <label class="option-label"><input type="radio" name="science" value="Claude"> Claude</label>
                <label class="option-label"><input type="radio" name="science" value="Gemini"> Gemini</label>
                <label class="option-label"><input type="radio" name="science" value="Copilot"> Microsoft Copilot</label>
            </div>

            <div class="question-block">
                <div class="question-title">4. What AI source do you find the most useful for Computer Science work?</div>
                <label class="option-label"><input type="radio" name="cs" value="ChatGPT" required> ChatGPT</label>
                <label class="option-label"><input type="radio" name="cs" value="Claude"> Claude</label>
                <label class="option-label"><input type="radio" name="cs" value="Gemini"> Gemini</label>
                <label class="option-label"><input type="radio" name="cs" value="Copilot"> Microsoft Copilot</label>
            </div>

            <div class="question-block">
                <div class="question-title">5. What AI source do you find the most useful for History work?</div>
                <label class="option-label"><input type="radio" name="history" value="ChatGPT" required> ChatGPT</label>
                <label class="option-label"><input type="radio" name="history" value="Claude"> Claude</label>
                <label class="option-label"><input type="radio" name="history" value="Gemini"> Gemini</label>
                <label class="option-label"><input type="radio" name="history" value="Copilot"> Microsoft Copilot</label>
            </div>

            <div class="question-block">
                <div class="question-title">6. Do you use AI to help you with schoolwork in essays and assignments?</div>
                <label class="option-label"><input type="radio" name="useAI" value="Yes" required> Yes</label>
                <label class="option-label"><input type="radio" name="useAI" value="No"> No</label>
            </div>

            <div class="question-block">
                <div class="question-title">7. Most classes do not want students to use AI. What do you feel about these policies? How would you want to use AI without having it do everything for you and it being considered cheating?</div>
                <textarea name="frq" placeholder="Share your thoughts here..." required></textarea>
            </div>

            <button onclick="submitSurvey()">Submit Survey</button>
        </div>
        
        <div class="results-section" id="resultsSection">
            <h2 style="text-align: center; color: #333; margin-bottom: 30px;">Survey Results</h2>
            
            <div class="chart-container">
                <h3>English</h3>
                <canvas id="englishChart"></canvas>
            </div>
            
            <div class="chart-container">
                <h3>Math</h3>
                <canvas id="mathChart"></canvas>
            </div>
            
            <div class="chart-container">
                <h3>Science</h3>
                <canvas id="scienceChart"></canvas>
            </div>
            
            <div class="chart-container">
                <h3>Computer Science</h3>
                <canvas id="csChart"></canvas>
            </div>
            
            <div class="chart-container">
                <h3>History</h3>
                <canvas id="historyChart"></canvas>
            </div>
            
            <div class="chart-container">
                <h3>Do Students Use AI for Schoolwork?</h3>
                <canvas id="useAIChart"></canvas>
            </div>
            
            <div id="resultsRecentFRQs"></div>
        </div>
    </div>

    <script>
        let charts = {};
        
        async function loadSurveyData() {
            try {
                const response = await fetch('/api/survey');
                const data = await response.json();
                displayRecentFRQs(data.frqs.slice(0, 3), 'recentFRQs');
            } catch (error) {
                console.error('Error loading survey data:', error);
            }
        }
        
        function displayRecentFRQs(frqs, containerId) {
            const container = document.getElementById(containerId);
            if (frqs.length === 0) {
                container.innerHTML = '';
                return;
            }
            
            let html = '<div class="recent-frqs"><h3>Recent Student Thoughts:</h3>';
            frqs.forEach(frq => {
                const date = new Date(frq.timestamp).toLocaleString();
                html += `
                    <div class="frq-item">
                        <div class="frq-text">${frq.text}</div>
                        <div class="frq-time">${date}</div>
                    </div>
                `;
            });
            html += '</div>';
            container.innerHTML = html;
        }
        
        async function submitSurvey() {
            const formData = {
                english: document.querySelector('input[name="english"]:checked')?.value,
                math: document.querySelector('input[name="math"]:checked')?.value,
                science: document.querySelector('input[name="science"]:checked')?.value,
                cs: document.querySelector('input[name="cs"]:checked')?.value,
                history: document.querySelector('input[name="history"]:checked')?.value,
                useAI: document.querySelector('input[name="useAI"]:checked')?.value,
                frq: document.querySelector('textarea[name="frq"]').value
            };
            
            if (!formData.english || !formData.math || !formData.science || !formData.cs || !formData.history || !formData.useAI || !formData.frq) {
                alert('Please answer all questions before submitting.');
                return;
            }
            
            try {
                const response = await fetch('/api/survey', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(formData)
                });
                
                if (!response.ok) throw new Error('Failed to submit');
                
                const result = await response.json();
                
                document.getElementById('successMessage').style.display = 'block';
                document.getElementById('surveyForm').classList.add('hidden');
                document.getElementById('resultsSection').style.display = 'block';
                
                displayResults(result.data);
                displayRecentFRQs(result.data.frqs.slice(0, 3), 'resultsRecentFRQs');
                
                window.scrollTo({ top: document.getElementById('resultsSection').offsetTop - 20, behavior: 'smooth' });
                
            } catch (error) {
                console.error('Error:', error);
                alert('There was an error submitting your survey. Please try again.');
            }
        }
        
        function displayResults(data) {
            createChart('englishChart', 'English', data.english);
            createChart('mathChart', 'Math', data.math);
            createChart('scienceChart', 'Science', data.science);
            createChart('csChart', 'Computer Science', data.cs);
            createChart('historyChart', 'History', data.history);
            createChart('useAIChart', 'Use AI', data.useAI, '#2196F3');
        }
        
        function createChart(canvasId, label, data, color = '#4CAF50') {
            const ctx = document.getElementById(canvasId);
            
            if (charts[canvasId]) {
                charts[canvasId].destroy();
            }
            
            charts[canvasId] = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: Object.keys(data),
                    datasets: [{
                        label: 'Votes',
                        data: Object.values(data),
                        backgroundColor: color,
                        borderColor: color,
                        borderWidth: 1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                stepSize: 1
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            display: false
                        }
                    }
                }
            });
        }
        
        window.addEventListener('DOMContentLoaded', loadSurveyData);
    </script>
</body>
</html>
'''

if __name__ == '__main__':
    app.run(debug=True, port=5000)