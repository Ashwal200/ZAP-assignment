import time
import requests
import os
import pandas as pd
import numpy as np
TELEGRAM_TOKEN   = None
TELEGRAM_CHAT_ID = None

def send_telegram(message: str) -> None:
    """Send a message via Telegram bot. No-op if credentials are missing."""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}

    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        return

def notify_user(
    model_id: str,
    phone_number: str,
    desired_price: float,
    description: str,
    url: str,
) -> None:
    """
    Background stub: waits then sends a price-drop alert.
    In production, replace sleep with real polling/comparison logic.
    """

    # Simulate delay / polling cycle
    time.sleep(10)

    # Placeholder new price; in prod fetch current live price
    new_price = 1469.00

    drop_msg = (
        "🚨 Price Drop Alert!\n"
        f"Model: {model_id}\n"
        f"Description: {description}\n"
        f"Your Target: ₪{desired_price:.2f}\n"
        f"New Price Alert: ₪{new_price:.2f}\n"
        f"Link: {url}"
    )

    send_telegram(drop_msg)

def load_data():
    """Load and clean historical price data from CSV."""
    csv_path = os.path.join(os.path.dirname(__file__), "data/dataset.csv")
    df = pd.read_csv(csv_path, parse_dates=["date"])
    df = df.sort_values("date")
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df = df.dropna(subset=["price"])
    df["day_index"] = np.arange(len(df))
    return df