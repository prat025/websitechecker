import hashlib
import requests
import time
import os
from bs4 import BeautifulSoup
from flask import Flask
import threading

# Settings
URL = 'https://upsc.gov.in/examinations/Civil%20Services%20%28Preliminary%29%20Examination%2C%202025'  # Replace with your target website
CHECK_INTERVAL = 60 * 5  # Time between checks in seconds (10 minutes)
HASH_FILE = 'website_hash.txt'
TELEGRAM_BOT_TOKEN = '123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11'
TELEGRAM_CHAT_ID = '5614373396'

def get_clean_website_html(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove dynamic elements
        for tag in soup(['script', 'style', 'noscript']):
            tag.decompose()

        # Remove the footer
        footer = soup.select_one('body > footer')
        if footer:
            footer.decompose()

        return soup.get_text().strip()
    except requests.RequestException as e:
        print(f"Error fetching website: {e}")
        return None

def get_website_hash(url):
    clean_text = get_clean_website_html(url)
    if clean_text is None:
        return None
    return hashlib.sha256(clean_text.encode('utf-8')).hexdigest()

def read_last_hash():
    if not os.path.exists(HASH_FILE):
        return None
    with open(HASH_FILE, 'r') as file:
        return file.read().strip()

def save_current_hash(current_hash):
    with open(HASH_FILE, 'w') as file:
        file.write(current_hash)


def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot8133601625:AAHxOFyujPLvjfpufuX19m_JdluejKcxve0/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        print("✅ Telegram alert sent.")
    except requests.RequestException as e:
        print(f"❌ Failed to send Telegram message: {e}")

def check_for_update():
    current_hash = get_website_hash(URL)
    if current_hash is None:
        return

    last_hash = read_last_hash()

    if last_hash != current_hash:
        print("🔔 Website has been updated!")
        send_telegram_alert(f"🔔 The website {URL} has been updated.")
        save_current_hash(current_hash)
    else:
        print("✅ No change detected.")

def monitor_website():
    print("🔍 Starting website monitoring...")
    while True:
        check_for_update()
        time.sleep(CHECK_INTERVAL)

app = Flask(__name__)

@app.route("/")
def home():
    return "App is running"

if __name__ == "__main__":
    threading.Thread(target=monitor_website, daemon=True).start()
    app.run(host="0.0.0.0", port=10000)

