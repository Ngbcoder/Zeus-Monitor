#!/usr/bin/env python3
import os, subprocess
from flask import Flask, request, render_template_string, redirect
from dotenv import load_dotenv, set_key

env_path = "/home/npi/uno/.env"
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)

HTML_BASE = """
<!DOCTYPE html>
<html>
<head>
    <title>Zeus LCD Config</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body { font-family: sans-serif; padding: 20px; background: #f0f2f5; margin: 0; }
        textarea { width: 100%; height: 500px; font-family: monospace; background: #1e1e1e; color: #9cdcfe; padding: 10px; border: none; box-sizing: border-box; border-radius: 4px; }
        .card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); max-width: 800px; margin: auto; }
        nav { margin-bottom: 15px; font-weight: bold; }
        nav a { text-decoration: none; color: #007bff; margin-right: 15px; }
        button { cursor: pointer; padding: 10px 20px; border-radius: 4px; border: 1px solid #ccc; background: #fff; margin-top: 10px; }
        .primary { background: #007bff; color: white; border: none; }
        .update { background: #28a745; color: white; border: none; }
        input { padding: 8px; margin-bottom: 15px; width: 100%; max-width: 300px; display: block; border: 1px solid #ddd; border-radius: 4px; }
        hr { border: 0; border-top: 1px solid #eee; margin: 20px 0; }
    </style>
</head>
<body>
    <div class="card">
        <nav><a href="/">⚙️ Config</a> | <a href="/editor">📝 Editor</a></nav><hr>
        {{ content | safe }}
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    # Refresh env from disk for the UI
    load_dotenv(dotenv_path=env_path, override=True)
    content = f'''
    <h2>Configuration</h2>
    <form method="POST" action="/save">
        <label>Location:</label>
        <input name="LOCATION" value="{os.getenv('LOCATION', '')}">
        <label>Sleep Hour (24h format):</label>
        <input type="number" name="SLEEP_HOUR" value="{os.getenv('SLEEP_HOUR', '22')}">
        <button type="submit" class="primary">Save Changes</button>
    </form>
    <hr>
    <h3>System Tools</h3>
    <form action="/update" method="POST">
        <button type="submit" class="update">Pull GitHub & Restart Service</button>
    </form>
    '''
    return render_template_string(HTML_BASE.replace('{{ content | safe }}', content))

@app.route('/save', methods=['POST'])
def save():
    for k in ['LOCATION', 'SLEEP_HOUR']:
        if k in request.form: 
            set_key(env_path, key=k, value=request.form[k])
    # Restart the worker service to apply new settings immediately
    subprocess.Popen(["sudo", "systemctl", "restart", "uno-monitor.service"])
    return redirect('/')

@app.route('/update', methods=['POST'])
def update():
    try:
        subprocess.run(["git", "pull", "origin", "main"], cwd="/home/npi/uno", check=True)
        subprocess.Popen(["sudo", "systemctl", "restart", "uno-monitor.service"])
        return "Updating from GitHub... The service will restart in a moment."
    except Exception as e:
        return f"Update failed: {str(e)}"

@app.route('/editor', methods=['GET', 'POST'])
def editor():
    file_path = "/home/npi/uno/worker.py" # Now editing the logic file
    if request.method == 'POST':
        with open(file_path, 'w') as f: 
            f.write(request.form['code'])
        subprocess.Popen(["sudo", "systemctl", "restart", "uno-monitor.service"])
        return "Logic Updated! Restarting worker..."
    
    with open(file_path, 'r') as f: 
        code = f.read()
    content = f'''
    <h2>Logic Editor (worker.py)</h2>
    <form method="POST">
        <textarea name="code">{code}</textarea><br>
        <button type="submit" class="primary">Save & Restart Worker</button>
    </form>
    '''
    return render_template_string(HTML_BASE.replace('{{ content | safe }}', content))

if __name__ == "__main__":
    # Host on 0.0.0.0 so you can access it via Pi's IP on your network
    app.run(host='0.0.0.0', port=5000, debug=False)