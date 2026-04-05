import os
import requests
import pandas as pd
import asyncio
import json
import time
from datetime import datetime
from dotenv import load_dotenv
import requests

load_dotenv()

TELEGRAM_TOKEN = "8646751152:AAEbhd4LVGhBJjfDFMDTrCixnL1E_owKapY"
CHAT_ID = "818347325"

GAMMA_API_URL = "https://gamma-api.polymarket.com/markets"


def fetch_markets():
    response = requests.get(GAMMA_API_URL)
    return response.json()


def extract_opportunities(markets):
    results = []   # ✅ VERY IMPORTANT

    for m in markets:
        try:
            price = float(m.get("outcomes", [{}])[0].get("price", 0))
            liquidity = float(m.get("liquidity", 0))
            volume = float(m.get("volume24hr", 0))
        except:
            continue

        if 0.70 <= price <= 0.90 and liquidity >= 20000:
            results.append({
                "question": m.get("question"),
                "price": price,
                "volume": volume,
                "liquidity": liquidity
            })

    # ✅ ADD THIS ALSO (YOU ARE MISSING IT)
    results = sorted(results, key=lambda x: x["volume"], reverse=True)

    return results[:3]





def format_message(opps):
    if not opps:
        return "No trades today."

    msg = f"📊 Safety Scan\n{datetime.utcnow()}\n\n"

    for i, o in enumerate(opps[:5], 1):
        msg += f"{i}. {o['question']}\n"
        msg += f"→ {o['outcome']} @ {o['price']:.2f}\n"
        msg += f"💧 {o['liquidity']} | 📈 {o['volume']}\n\n"

    return msg


async def send_async(msg):
    bot = Bot(token=TELEGRAM_TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text=msg)


import requests

def send(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    payload = {
        "chat_id": CHAT_ID,
        "text": text
    }

    response = requests.post(url, json=payload)
    print(response.text)


def load_sent():
    try:
        with open("sent.json", "r") as f:
            return json.load(f)
    except:
        return []


def save_sent(data):
    with open("sent.json", "w") as f:
        json.dump(data, f)


def run():
    send("✅ BOT IS ACTIVE")

    markets = fetch_markets()
    opps = extract_opportunities(markets)

    if not opps:
    send("ℹ️ Bot checked — no strong trades right now.")
    return

    message = "🔥 TOP POLYMARKET TRADES\n\n"

    for o in opps:
        message += f"📊 {o['question']}\n"
        message += f"💰 Price: {round(o['price'] * 100)}%\n"
        message += f"📈 Volume: ${int(o['volume'])}\n"
        message += "-------------------\n"

    send(message)


if __name__ == "__main__":
    while True:
        run()
        time.sleep(900)  # 900 seconds = 15 minutes