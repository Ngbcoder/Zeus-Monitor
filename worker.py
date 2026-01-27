#!/usr/bin/env python3
import os, imaplib, serial, serial.tools.list_ports, time, requests, pytz
from datetime import datetime
from dotenv import load_dotenv

env_path = "/home/npi/uno/.env"
load_dotenv(dotenv_path=env_path)
local_tz = pytz.timezone("America/New_York")

WEATHER_CODES = {
    1000: "Clear", 1100: "Mostly Clear", 1101: "Partly Cloudy", 
    1102: "Mostly Cloudy", 1001: "Cloudy", 4000: "Drizzle",
    4001: "Rain", 4200: "Light Rain", 4201: "Heavy Rain",
    5000: "Snow", 8000: "Thunderstorm"
}

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
    TARGET_ID = "1"
    try:
        api_url = os.getenv('Kuma_IP')
        response = requests.get(api_url, timeout=3)
        data = response.json()
        heartbeats = data.get('heartbeatList', {}).get(TARGET_ID, [])
        if heartbeats:
            status = heartbeats[-1].get('status')
            return {1: "ONLINE", 0: "OFFLINE", 2: "PENDING"}.get(status, "UNKNOWN")
        return "NOT FOUND"
    except: return "CONN ERR"

def get_weather():
    try:
        loc = os.getenv('LOCATION', 'Corinna,ME')
        api = os.getenv('TOMORROW_API_KEY')
        url = f"https://api.tomorrow.io/v4/weather/realtime?location={loc}&apikey={api}&units=imperial"
        data = requests.get(url, timeout=5).json()
        val = data['data']['values']
        return f"{round(val['temperature'])}F", WEATHER_CODES.get(val['weatherCode'], "Cloudy")
    except: return "Err", "No Data"

def lcd_worker():
    while True:
        ports = serial.tools.list_ports.comports()
        port = next((p.device for p in ports if any(x in p.device for x in ["ACM", "USB"])), None)
        if not port:
            time.sleep(5); continue
        try:
            ser = serial.Serial(port, 9600, timeout=1)
            time.sleep(2) # Wait for Arduino reset
            while True:
                now = datetime.now(local_tz)
                sleep_hr = int(os.getenv('SLEEP_HOUR', 22))
                
                if now.hour >= sleep_hr or now.hour < 7:
                    ser.write(b"BL_OFF\n")
                    time.sleep(30)
                else:
                    ser.write(b"BL_ON\n")
                    # Screen 1: Clock (Updates every second for 10 seconds)
                    for _ in range(10):
                        t = datetime.now(local_tz)
                        line1 = t.strftime("%I:%M %p").ljust(16)
                        line2 = t.strftime("%a, %b %d").ljust(16)
                        ser.write(f"{line1}|{line2}\n".encode())
                        time.sleep(1)
                    
                    # Screen 2: Status
                    unread, kuma = get_unread_count(), get_kuma_status()
                    ser.write(f"Mail: {unread[:10]:<10}|Kuma: {kuma[:10]:<10}\n".encode())
                    time.sleep(5)
                    
                    # Screen 3: Weather
                    temp, cond = get_weather()
                    ser.write(f"Maine: {temp:<9}|{cond[:16]:<16}\n".encode())
                    time.sleep(5)
        except Exception: 
            time.sleep(5)

if __name__ == "__main__":
    lcd_worker()