import time
import requests
import numpy as np
import os
from datetime import datetime

# ====== CONFIG ======
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "https://discord.com/api/webhooks/xxxxxx/xxxxx")
SYMBOL = os.getenv("SYMBOL", "BTCUSDT")
INTERVAL = os.getenv("INTERVAL", "15m")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "60"))
ALPHA_LENGTH = int(os.getenv("ALPHA_LENGTH", "14"))
SMOOTH = int(os.getenv("SMOOTH", "1"))

# ====== LẤY DỮ LIỆU TỪ BINANCE ======
def get_binance_data(symbol="BTCUSDT", interval="15m", limit=500):
    url = "https://api.binance.com/api/v3/klines"
    params = {"symbol": symbol, "interval": interval, "limit": limit}
    data = requests.get(url, params=params).json()
    
    # Chuyển thành numpy arrays
    opens = np.array([float(d[1]) for d in data])
    highs = np.array([float(d[2]) for d in data])
    lows = np.array([float(d[3]) for d in data])
    closes = np.array([float(d[4]) for d in data])
    
    return {
        'open': opens,
        'high': highs,
        'low': lows,
        'close': closes
    }

# ====== ALPHATREND ======
def alpha_trend(data, length=14, smooth=1):
    highs = data['high']
    lows = data['low']
    closes = data['close']
    n = len(closes)
    
    # Tính ATR đơn giản (rolling max-min)
    atr = np.zeros(n)
    for i in range(length, n):
        atr[i] = np.max(highs[i-length:i]) - np.min(lows[i-length:i])
    
    upT = lows - atr * smooth
    downT = highs + atr * smooth
    trend = np.zeros(n)
    
    last_trend = 0
    for i in range(1, n):
        if closes[i] > downT[i - 1]:
            last_trend = 1  # BUY
        elif closes[i] < upT[i - 1]:
            last_trend = -1  # SELL
        trend[i] = last_trend
    
    data['trend'] = trend
    return data

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
    print(f"🚀 Bot AlphaTrend đã khởi động!")
    print(f"📈 Symbol: {SYMBOL}")
    print(f"⏱️  Interval: {INTERVAL}")
    print(f"🔄 Kiểm tra mỗi: {CHECK_INTERVAL}s")
    print("-" * 50)

    while True:
        try:
            print(f"⏰ Kiểm tra tín hiệu lúc {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            data = get_binance_data(SYMBOL, INTERVAL)
            data = alpha_trend(data, ALPHA_LENGTH, SMOOTH)

            current_trend = data['trend'][-1]
            current_price = data['close'][-1]
            
            signal = "BUY" if current_trend == 1 else "SELL" if current_trend == -1 else None
            
            print(f"📊 Giá hiện tại: ${current_price:,.2f} | Tín hiệu: {signal}")

            if signal and signal != last_signal:
                print(f"🔔 Phát hiện tín hiệu mới: {signal}")
                send_discord_alert(signal, current_price)
                last_signal = signal

        except Exception as e:
            print(f"❌ Error in main loop: {e}")

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
