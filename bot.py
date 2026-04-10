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
    results = []

    for m in markets:
        question = str(m.get("question", "")).lower()

        allowed_keywords = [
            "weather", "rain", "temperature", "storm",
            "climate", "warming",
            "war", "election", "president", "china", "russia", "usa",
            "bitcoin", "btc", "ethereum", "eth", "crypto",
            "stock", "nasdaq", "s&p", "dow",
            "match", "team", "league", "goal", "football", "nba", "soccer"
        ]

        if not any(k in question for k in allowed_keywords):
            continue

        try:
            outcomes = m.get("outcomes", [])
            price = float(outcomes[0].get("price", 0)) if outcomes else 0
            liquidity = float(m.get("liquidity", 0))
            volume = float(m.get("volume24hr", 0))
        except Exception:
            continue

        edge = 0

        if volume > 100000:
            edge += 0.05

        if 0.70 <= price <= 0.90 and liquidity >= 20000 and edge >= 0.05:
            results.append({
                "question": m.get("question"),
                "price": price,
                "volume": volume,
                "liquidity": liquidity,
                "edge": edge
            })

    results = sorted(results, key=lambda x: x["volume"], reverse=True)

    return results[:3]


def format_message(opps):
    msg = "🔥 TOP POLYMARKET TRADES\n\n"

    for o in opps:
        question = o["question"].lower()

        # Detect category
        if any(x in question for x in ["btc", "bitcoin", "eth", "crypto"]):
            label = "₿ CRYPTO"
        elif any(x in question for x in ["stock", "nasdaq", "dow", "s&p"]):
            label = "📈 STOCKS"
        elif any(x in question for x in ["match", "team", "league", "goal", "football", "nba"]):
            label = "⚽ SPORTS"
        elif any(x in question for x in ["weather", "rain", "storm", "temperature"]):
            label = "🌦 WEATHER"
        elif any(x in question for x in ["climate", "warming"]):
            label = "🌍 CLIMATE"
        elif any(x in question for x in ["war", "election", "president", "china", "russia", "usa"]):
            label = "🌐 GEO"
        else:
            label = "📊 MARKET"

        msg += f"{label} TRADE\n"
        msg += f"📊 {o['question']}\n"
        msg += f"💰 Price: {o['price']*100:.0f}%\n"
        msg += f"📈 Volume: ${o['volume']:.0f}\n"
        msg += f"⚡ Edge: {o['edge']*100:.0f}%\n\n"

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
    markets = fetch_markets()
    opps = extract_opportunities(markets)

    if not opps:
        send("ℹ️ Checked market — no strong trades right now.")
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