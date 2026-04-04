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
    FILTER_TIERS = [(0.78, 0.85), (0.75, 0.88), (0.70, 0.90)]

    for min_price, max_price in FILTER_TIERS:
        temp = []

        for market in markets:
            try:
                liquidity = float(market.get("liquidity", 0))
                volume = float(market.get("volume24hr", 0))
                question = market.get("question", "")
                outcomes = market.get("outcomes", [])

                if liquidity < 50000:
                    continue

                for o in outcomes:
                    price = float(o.get("price", 0))

                    if min_price <= price <= max_price:
                        temp.append({
                            "question": question,
                            "outcome": o.get("name"),
                            "price": price,
                            "liquidity": liquidity,
                            "volume": volume
                        })
            except:
                continue

        if temp:
            return temp

    return []


def rank_opportunities(opps):
    df = pd.DataFrame(opps)
    if df.empty:
        return []
    return df.sort_values(by="volume", ascending=False).to_dict("records")


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
    markets = fetch_markets()
    opps = extract_opportunities(markets)
    ranked = rank_opportunities(opps)

    sent = load_sent()
    new = [o for o in ranked if o['question'] not in sent]

    if new:
        message = format_message(new)
        send(message)
        save_sent(sent + [o['question'] for o in new])
    else:
        send("🚫 No new trades today.")


if __name__ == "__main__":
    import time

    while True:
        run()
        time.sleep(60)