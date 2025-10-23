import time
import requests
import pandas as pd
from datetime import datetime
from binance.client import Client

# ====== CONFIG ======
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/xxxxxx/xxxxx"  # <-- thay bằng webhook thật
SYMBOL = "BTCUSDT"
INTERVAL = "15m"
CHECK_INTERVAL = 60  # 60 giây kiểm tra 1 lần
ALPHA_LENGTH = 14
SMOOTH = 1

# ====== LẤY DỮ LIỆU TỪ BINANCE ======
def get_binance_data(symbol="BTCUSDT", interval="15m", limit=500):
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    data = requests.get(url, params=params).json()

    df = pd.DataFrame(data, columns=[
        "open_time", "open", "high", "low", "close", "volume",
        "close_time", "qav", "num_trades", "taker_base_vol",
        "taker_quote_vol", "ignore"
    ])

    df["open"] = df["open"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["close"] = df["close"].astype(float)
    df["volume"] = df["volume"].astype(float)
    df["time"] = pd.to_datetime(df["open_time"], unit="ms")
    return df[["time", "open", "high", "low", "close", "volume"]]

# ====== ALPHATREND ======
def alpha_trend(df, length=14, smooth=1):
    df = df.copy()
    df['atr'] = df['high'].rolling(length).max() - df['low'].rolling(length).min()
    df['upT'] = df['low'] - df['atr'] * smooth
    df['downT'] = df['high'] + df['atr'] * smooth
    df['trend'] = 0

    last_trend = 0
    for i in range(1, len(df)):
        if df['close'].iloc[i] > df['downT'].iloc[i - 1]:
            last_trend = 1  # BUY
        elif df['close'].iloc[i] < df['upT'].iloc[i - 1]:
            last_trend = -1  # SELL
        df.loc[df.index[i], 'trend'] = last_trend
    return df

# ====== GỬI TÍN HIỆU ĐẾN DISCORD ======
def send_discord_alert(signal_type, price):
    color = 0x00ff00 if signal_type == "BUY" else 0xff0000
    data = {
        "embeds": [{
            "title": f"{signal_type} Signal on BTC/USDT (M15)",
            "description": f"**Price:** {price:.2f} USD\n**Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "color": color
        }]
    }
    try:
        requests.post(DISCORD_WEBHOOK_URL, json=data)
        print(f"[{datetime.now()}] Sent {signal_type} alert at {price:.2f}")
    except Exception as e:
        print("Error sending Discord alert:", e)

# ====== MAIN LOOP ======
def main():
    last_signal = None

    while True:
        try:
            df = get_binance_data(SYMBOL, INTERVAL)
            df = alpha_trend(df, ALPHA_LENGTH, SMOOTH)

            last_row = df.iloc[-1]
            signal = "BUY" if last_row["trend"] == 1 else "SELL" if last_row["trend"] == -1 else None

            if signal and signal != last_signal:
                send_discord_alert(signal, last_row["close"])
                last_signal = signal

        except Exception as e:
            print("Error in main loop:", e)

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
