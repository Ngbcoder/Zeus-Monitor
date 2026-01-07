

## ⚡ Zeus Monitor

A modular, high-visibility system monitor for Raspberry Pi. Zeus bridges the gap between a modern web-based dashboard and a physical 16x2 LCD display, giving you a dedicated "at-a-glance" window into your home lab or desktop setup.

I built this because I wanted a way to see my notifications, weather, and server status without having to open a browser tab or check my phone. With the new plugin system, you can pull in just about any data you care about.

##  ✨ What it does

Hybrid Dashboard: View stats on a physical I2C LCD or through a sleek, responsive web UI.

Easy Plugins: Want to see Bitcoin prices? Pi-hole stats? Just drop a small Python script into the plugins/ folder. It just works.

GitHub Sync: Found a cool plugin on GitHub? Paste the repo URL into the dashboard and Zeus will install it for you.

Service Monitoring: Hooks directly into Uptime Kuma to tell you if your servers are breathing.

Life Integrations:

Email: Keeps an eye on your inbox (IMAP).

Weather: Real-time temp and conditions via Tomorrow.io.

Reading List: Shows your current progress toward your Goodreads yearly goal.

Smart Backlight: It automatically dims the LCD at night so you can sleep, with a manual override for when you're pulling an all-nighter.

Web Editor: Fix bugs or tweak logic right from the browser—no SSH required for quick edits.

🛠️ Setting it up

1. Install UV for fast python 
`wget -qO- https://astral.sh/uv/install.sh | sh`

2. Use UV to install Python
`uv  python  install`

3. Make sure python is installed
`python3.13`

4.  Grab the code

`cd /home/npi git clone  [git@github.com](mailto:git@github.com):Ngbcoder/Arudino-Terminal.git uno cd uno`

5.  Install the essentials

`uv add flask pyserial pytz python-dotenv requests docker`

6.  Configure your environment

Create a .env file in the root directory. This is where the magic (and your API keys) lives:

`EMAIL_USER=[your_email@gmail.com] 
EMAIL_PASS=your_app_password 
EMAIL_IMAP=imap.gmail.com 
KUMA_ID=1 
LOCATION=City,State 
TOMORROW_API_KEY=your_api_key 
GOODREADS_RSS=your_rss_url THEME=midnight`

7.  Make it a Service

To make sure Zeus starts up whenever your Pi boots:

`sudo nano /etc/systemd/system/uno-monitor.service`

Paste this in (just double-check that your paths are correct):

`[Unit] Description=Zeus Monitor Service After=network.target
[Service] ExecStart=/usr/bin/python3 /home/npi/uno/main.py WorkingDirectory=/home/npi/uno StandardOutput=inherit StandardError=inherit Restart=always User=npi
[Install] WantedBy=multi-user.target`

Then fire it up:

`sudo systemctl enable uno-monitor.service sudo systemctl start uno-monitor.service`

🔌 Writing your own Plugins

Adding a new screen is dead simple. Just create a .py file in the plugins/ folder. Zeus looks for a function called `get_screen_data().`

Here’s a quick Bitcoin price example (btc.py):

`import requests`

`def get_screen_data(): try: r = requests.get("[https://api.coinbase.com/v2/prices/BTC-USD/spot](https://api.coinbase.com/v2/prices/BTC-USD/spot)", timeout=2) price = r.json()['data']['amount'] # Use "|" to split the top and bottom lines of the LCD return f"BTC Price: |${float(price):,.0f}" except: return "Crypto Error |Check Connection"`

🎨 Themes

The web UI comes with a few "flavors" to match your vibe:

Midnight: Deep blues and slates (The OG look).

Emerald: Clean, forest greens.

Cyberpunk: High-contrast black and neon green.

Crimson: Aggressive dark reds.

🤝 Contributions

If you find a bug or have a cool idea for a built-in feature, feel free to fork the repo and send over a pull request. Happy hacking!
