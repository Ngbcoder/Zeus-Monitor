#!/usr/bin/env python3
import os, imaplib, serial, serial.tools.list_ports, time, requests, pytz, threading, subprocess
from flask import Flask, request, render_template_string, redirect
from datetime import datetime
from dotenv import load_dotenv, set_key

# Load .env with an absolute path so the service doesn't lose it
load_dotenv(dotenv_path="~/uno/.env")
app = Flask(__name__)
local_tz = pytz.timezone("America/New_York")

WEATHER_CODES = {
    1000: "Clear", 1100: "Mostly Clear", 1101: "Partly Cloudy", 
    1102: "Mostly Cloudy", 1001: "Cloudy", 4000: "Drizzle",
    4001: "Rain", 4200: "Light Rain", 4201: "Heavy Rain",
    5000: "Snow", 8000: "Thunderstorm"
}

# --- DATA FETCHERS ---

def get_unread_count():
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(os.getenv('EMAIL_USER'), os.getenv('EMAIL_PASS'))
        mail.select("INBOX")
        _, resp = mail.search(None, 'UNSEEN')
        count = len(resp[0].split())
        mail.logout()
        return str(count)
    except: return "?"

def get_kuma_status():
    TARGET_ID = "1" # Your 'outerwebs' group ID
    try:
        api_url = os.getenv('Kuma_IP')
        response = requests.get(api_url, timeout=3)
        data = response.json()
        heartbeats = data.get('heartbeatList', {}).get(TARGET_ID, [])
        if heartbeats:
            last_status = heartbeats[-1].get('status')
            if last_status == 1: return "ONLINE"
            if last_status == 0: return "OFFLINE"
            if last_status == 2: return "PENDING"
        return "NOT FOUND"
    except: return "CONN ERR"

def get_weather():
    try:
        loc = os.getenv('LOCATION', 'Corinna,ME')
        api = os.getenv('TOMORROW_API_KEY')
        url = "https://api.tomorrow.io/v4/weather/realtime?location=" + loc + "&apikey=" + api + "&units=imperial"
        data = requests.get(url, timeout=5).json()
        val = data['data']['values']
        return str(round(val['temperature'])) + "F", WEATHER_CODES.get(val['weatherCode'], "Cloudy")
    except: return "Err", "No Data"

# --- WEB INTERFACE ---

HTML_BASE = """
<!DOCTYPE html>
<html>
<head><title>Zeus LCD</title><style>
    body { font-family: sans-serif; padding: 20px; background: #f0f2f5; }
    textarea { width: 100%; height: 500px; font-family: monospace; background: #1e1e1e; color: #9cdcfe; padding: 10px; }
    .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); max-width: 800px; margin: auto; }
</style></head>
<body>
    <div class="card">
        <nav><a href="/">Config</a> | <a href="/editor">Editor</a></nav><hr>
        {{ content | safe }}
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    content = '<h2>Config</h2><form method="POST" action="/save">'
    content += 'Location: <input name="LOCATION" value="' + os.getenv('LOCATION', '') + '"><br>'
    content += 'Sleep Hour: <input type="number" name="SLEEP_HOUR" value="' + os.getenv('SLEEP_HOUR', '22') + '"><br>'
    content += '<button type="submit">Save</button></form>'
    return render_template_string(HTML_BASE.replace('{{ content | safe }}', content))

@app.route('/save', methods=['POST'])
def save():
    for k in ['LOCATION', 'SLEEP_HOUR']:
        if k in request.form: set_key("/home/npi/uno/.env", key=k, value=request.form[k])
    return redirect('/')

@app.route('/editor', methods=['GET', 'POST'])
def editor():
    file_path = "/home/npi/uno/main.py"
    if request.method == 'POST':
        with open(file_path, 'w') as f: f.write(request.form['code'])
        subprocess.Popen(["sudo", "systemctl", "restart", "uno-monitor.service"])
        return "Saved! Restarting..."
    with open(file_path, 'r') as f: code = f.read()
    content = '<h2>Editor</h2><form method="POST"><textarea name="code">' + code + '</textarea><br><button type="submit">Save & Restart</button></form>'
    return render_template_string(HTML_BASE.replace('{{ content | safe }}', content))

# --- LCD WORKER ---

def lcd_worker():
    while True:
        ports = serial.tools.list_ports.comports()
        port = next((p.device for p in ports if "ACM" in p.device or "USB" in p.device), None)
        if not port:
            time.sleep(5); continue
        try:
            ser = serial.Serial(port, 9600, timeout=1)
            time.sleep(2)
            while True:
                now = datetime.now(local_tz)
                if now.hour >= int(os.getenv('SLEEP_HOUR', 22)) or now.hour < 7:
                    ser.write(b"BL_OFF\n")
                    time.sleep(60)
                else:
                    ser.write(b"BL_ON\n")
                    unread, kuma = get_unread_count(), get_kuma_status()
                    temp, cond = get_weather()
                    
                    # Screen 1 (Clock)
                    for _ in range(10):
                        t = datetime.now(local_tz)
                        ser.write((t.strftime("%I:%M %p").ljust(16) + "|" + t.strftime("%a, %b %d").ljust(16) + "\n").encode())
                        time.sleep(1)
                    # Screen 2 (Status)
                    ser.write((f"Mail: {unread}".ljust(16) + "|" + f"Kuma: {kuma}".ljust(16) + "\n").encode())
                    time.sleep(5)
                    # Screen 3 (Weather)
                    ser.write((f"Home: {temp}".ljust(16) + "|" + f"{cond}".ljust(16) + "\n").encode())
                    time.sleep(5)
        except: time.sleep(5)

if __name__ == "__main__":
    threading.Thread(target=lcd_worker, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)
