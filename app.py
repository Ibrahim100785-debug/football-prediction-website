import os
import requests
from datetime import datetime, timedelta
from flask import Flask, render_template

app = Flask(__name__)

# ========== KAYAN AIKIN ==========
# API key daga Bzzoiro (za mu sanya shi daga baya a Environment Variables)
BZZOIRO_API_KEY = os.environ.get('BZZOIRO_API_KEY', 'YOUR_API_KEY_HERE')
BZZOIRO_BASE_URL = "https://sports.bzzoiro.com/api/v1"
HEADERS = {"Authorization": f"Token {BZZOIRO_API_KEY}"}

def get_tomorrows_fixtures():
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    url = f"{BZZOIRO_BASE_URL}/events?date={tomorrow}"
    print(f"Fetching fixtures for {tomorrow}...")
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        r.raise_for_status()
        data = r.json()
        fixtures = data.get('results', [])
        print(f"Found {len(fixtures)} fixtures.")
        return fixtures
    except Exception as e:
        print(f"Error: {e}")
        return []

def filter_match(match):
    """Filter using low-risk system: prediction must be 'Home' or 'Away' and confidence >= 70%."""
    home = match.get('home_team', 'Unknown')
    away = match.get('away_team', 'Unknown')
    pred = match.get('prediction', '')  # 'Home', 'Draw', 'Away'
    conf = match.get('confidence', 0)
    if pred in ('Home', 'Away') and conf >= 70:
        return {
            'home': home,
            'away': away,
            'prediction': f"Double Chance: {home} or {away} (no draw)",
            'confidence': conf,
            'date': match.get('event_date', 'Date unknown')
        }
    return None

@app.route('/')
def home():
    fixtures = get_tomorrows_fixtures()
    good_matches = []
    for match in fixtures:
        filtered = filter_match(match)
        if filtered:
            good_matches.append(filtered)
    print(f"Filtered matches: {len(good_matches)}")
    return render_template('index.html', predictions=good_matches)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)