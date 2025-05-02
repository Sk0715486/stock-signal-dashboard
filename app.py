import streamlit as st
import pandas as pd
import requests
import time

API_KEY = "59bceecd5453253b2f318f184c7f93d9"
BASE_URL = "http://api.marketstack.com/v1/eod"

symbols = ["RELIANCE.XNSE", "INFY.XNSE", "TCS.XNSE", "SBIN.XNSE", "ICICIBANK.XNSE"]

def fetch_data(symbol):
    params = {
        "access_key": API_KEY,
        "symbols": symbol,
        "limit": 2,
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    if "data" not in data or len(data["data"]) < 2:
        return None
    today, yesterday = data["data"][0], data["data"][1]
    return {
        "symbol": symbol.replace(".XNSE", ""),
        "price_today": today["close"],
        "price_yesterday": yesterday["close"],
        "volume_today": today["volume"],
        "volume_yesterday": yesterday["volume"],
    }

def calculate_signal(stock):
    if not stock:
        return None
    price_change = (stock["price_today"] - stock["price_yesterday"]) / stock["price_yesterday"]
    volume_change = (stock["volume_today"] - stock["volume_yesterday"]) / stock["volume_yesterday"]
    if price_change > 0.01 and volume_change > 0.1:
        return "BUY"
    elif price_change < -0.01 and volume_change > 0.1:
        return "SELL"
    else:
        return "NEUTRAL"

def send_webhook(webhook_url, stock):
    data = {
        "symbol": stock["symbol"],
        "signal": stock["signal"],
        "price_today": stock["price_today"],
        "price_yesterday": stock["price_yesterday"],
        "volume_today": stock["volume_today"],
        "volume_yesterday": stock["volume_yesterday"],
    }
    try:
        requests.post(webhook_url, json=data)
    except Exception as e:
        st.warning(f"Webhook failed: {e}")

def main():
    st.title("Live Stock Signal Dashboard + Webhook")
    st.caption("Auto-refresh every 60 seconds | Data Source: Marketstack")

    webhook_url = st.text_input("Webhook URL (optional):", "")
    refresh = st.button("Refresh Now")

    if refresh or webhook_url != "":
        results = []
        for symbol in symbols:
            data = fetch_data(symbol)
            if data:
                signal = calculate_signal(data)
                data["signal"] = signal
                results.append(data)
                if webhook_url and signal in ["BUY", "SELL"]:
                    send_webhook(webhook_url, data)

        df = pd.DataFrame(results)
        st.dataframe(df[["symbol", "price_today", "price_yesterday", "volume_today", "volume_yesterday", "signal"]])
        st.caption("Last updated: " + time.strftime('%Y-%m-%d %H:%M:%S'))

if __name__ == "__main__":
    main()