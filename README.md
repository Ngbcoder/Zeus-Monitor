## ⚡ Zeus Monitor

A modular, high-visibility system monitor for Raspberry Pi. Zeus bridges the gap between a modern web-based dashboard and a physical 16x2 LCD display, giving you a dedicated "at-a-glance" window into your home lab or desktop setup.

I built this because I wanted a way to see my notifications, weather, and server status without having to open a browser tab or check my phone. With the plugin system, you can pull in just about any data you care about.

# ⌨️ Hardware

-   1 Raspberry PI (I use the model 3 but any should do)
    
-   1 Arduino Uno (For driving the display)
    
-   1 I2C Display 16X2 (Recommended)
    

# 📦 Case

I made a 3D-printable case for this setup: [View on Thingiverse](https://www.thingiverse.com/thing:7276552/files "null")

## ✨ What it does

-   **Hybrid Dashboard:** View stats on a physical I2C LCD or through a sleek, responsive web UI.
    
-   **Easy Plugins:** Want to see Bitcoin prices? Pi-hole stats? Just drop a small Python script into the `plugins/` folder. It just works.
    
-   **GitHub Sync:** Found a cool plugin on GitHub? Paste the repo URL into the dashboard and Zeus will install it for you.
    
-   **Service Monitoring:** Hooks directly into Uptime Kuma to tell you if your servers are breathing.
    
-   **Life Integrations:**
    
    -   **Email:** Keeps an eye on your inbox (IMAP).
        
    -   **Weather:** Real-time temp and conditions via Tomorrow.io.
        
    -   **Reading List:** Shows your current progress toward your Goodreads yearly goal.
        
-   **Smart Backlight:** It automatically dims the LCD at night so you can sleep, with a manual override for when you're pulling an all-nighter.
    
-   **Web Editor:** Fix bugs or tweak logic right from the browser—no SSH required for quick edits.
    

## 🛠️ Setting it up

1.  **Install UV for fast Python management**
    
    ```
    wget -qO- [https://astral.sh/uv/install.sh](https://astral.sh/uv/install.sh) | sh
    
    ```
    
2.  **Use UV to install Python**
    
    ```
    uv python install
    
    ```
    
3.  **Verify Installation**
    
    ```
    python3.13 --version
    
    ```
    
4.  **Grab the code**
    
    ```
    cd /home/npi
    git clone git@github.com:Ngbcoder/Arudino-Terminal.git uno
    cd uno
    
    ```
    
5.  **Install the essentials**
    
    ```
    uv add flask pyserial pytz python-dotenv requests docker
    
    ```
    
6.  **Configure your environment** Create a `.env` file in the root directory:
    
    ```
    EMAIL_USER=your_email@gmail.com
    EMAIL_PASS=your_app_password
    Kuma_IP=http://your-kuma-api-url
    LOCATION=City,State
    TOMORROW_API_KEY=your_api_key
    SLEEP_HOUR=22
    THEME=midnight
    
    ```
    
7.  **Permissions (Serial Access)** Ensure your user can talk to the Arduino:
    
    ```
    sudo usermod -a -G dialout $USER
    # Note: You may need to log out and back in for this to take effect.
    
    ```
    
8.  **Make it a Service** To ensure Zeus starts on boot, link the service file from your repo to the system:
    
    ```
    # Create a symbolic link
    sudo ln -s /home/npi/uno/uno-monitor.service /etc/systemd/system/uno-monitor.service
    
    # Reload and Start
    sudo systemctl daemon-reload
    sudo systemctl enable uno-monitor.service
    sudo systemctl start uno-monitor.service
    
    ```
    

## 📟 Service Management

-   **Check Status:** `sudo systemctl status uno-monitor.service`
    
-   **View Live Logs:** `journalctl -u uno-monitor.service -f`
    
-   **Restart:** `sudo systemctl restart uno-monitor.service`
    

## 🔌 Writing your own Plugins

Adding a new screen is dead simple. Just create a `.py` file in the `plugins/` folder. Zeus looks for a function called `get_screen_data()`.

**Example: Bitcoin Price (btc.py)**

```
import requests

def get_screen_data():
    try:
        r = requests.get("[https://api.coinbase.com/v2/prices/BTC-USD/spot](https://api.coinbase.com/v2/prices/BTC-USD/spot)", timeout=2)
        price = r.json()['data']['amount']
        # Use "|" to split the top and bottom lines of the LCD
        return f"BTC Price:|${float(price):,.0f}"
    except:
        return "Crypto Error|Check Connection"

```

## 🎨 Themes

The web UI comes with a few "flavors" to match your vibe:

-   **Midnight:** Deep blues and slates (The OG look).
    
-   **Emerald:** Clean, forest greens.
    
-   **Cyberpunk:** High-contrast black and neon green.
    
-   **Crimson:** Aggressive dark reds.
    

## 🤝 Contributions

If you find a bug or have a cool idea for a built-in feature, feel free to fork the repo and send over a pull request. Happy hacking!