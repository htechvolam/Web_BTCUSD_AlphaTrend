import time
import requests
import numpy as np
import os
from datetime import datetime
from flask import Flask, jsonify, render_template
from threading import Thread

# ====== CONFIG ======
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "https://discord.com/api/webhooks/xxxxxx/xxxxx")
SYMBOL = os.getenv("SYMBOL", "BTCUSDT")
INTERVAL = os.getenv("INTERVAL", "15m")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", "60"))
ALPHA_LENGTH = int(os.getenv("ALPHA_LENGTH", "14"))
SMOOTH = int(os.getenv("SMOOTH", "1"))
PORT = int(os.getenv("PORT", "10000"))

# ====== FLASK APP ======
app = Flask(__name__)
bot_status = {
    "status": "starting",
    "last_check": None,
    "last_signal": None,
    "current_price": None
}

# Lưu lịch sử tín hiệu và giá
signal_history = []  # [{timestamp, signal, price, profit}]
price_history = []   # [{timestamp, price}]
max_history = 100    # Giữ tối đa 100 records

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

# ====== FLASK ROUTES ======
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/health')
def health():
    return jsonify({"status": "ok"}), 200

@app.route('/api/status')
def api_status():
    return jsonify({
        "status": bot_status["status"],
        "symbol": SYMBOL,
        "interval": INTERVAL,
        "last_check": bot_status["last_check"],
        "last_signal": bot_status["last_signal"],
        "current_price": bot_status["current_price"]
    })

@app.route('/api/history')
def api_history():
    return jsonify({
        "signals": signal_history
    })

@app.route('/api/chart')
def api_chart():
    # Lấy 50 giá gần nhất từ price_history
    recent_prices = price_history[-50:] if len(price_history) > 0 else []
    
    labels = [p["timestamp"] for p in recent_prices]
    prices = [p["price"] for p in recent_prices]
    
    return jsonify({
        "labels": labels,
        "prices": prices
    })

@app.route('/api/backtest')
def api_backtest():
    from flask import request
    
    # Lấy tham số từ query string
    days = request.args.get('days', default=7, type=int)
    
    try:
        # Tính số nến cần lấy (mỗi nến 15 phút, 96 nến/ngày)
        limit = min(days * 96, 1000)  # Giới hạn tối đa 1000 nến
        
        # Lấy dữ liệu lịch sử
        data = get_binance_data(SYMBOL, INTERVAL, limit=limit)
        data = alpha_trend(data, ALPHA_LENGTH, SMOOTH)
        
        # Chạy backtest
        results = run_backtest(data)
        
        return jsonify({
            "success": True,
            "period": f"{days} days",
            "total_candles": len(data['close']),
            **results
        })
        
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

def run_backtest(data):
    """
    Chạy backtest trên dữ liệu lịch sử
    """
    closes = data['close']
    trends = data['trend']
    
    trades = []
    current_position = None  # None, 'BUY', 'SELL'
    entry_price = None
    total_profit = 0
    wins = 0
    losses = 0
    
    for i in range(1, len(closes)):
        current_trend = trends[i]
        prev_trend = trends[i-1]
        price = closes[i]
        
        # Phát hiện thay đổi tín hiệu
        if current_trend != prev_trend and current_trend != 0:
            signal = "BUY" if current_trend == 1 else "SELL"
            
            # Đóng position cũ và tính profit
            if current_position and entry_price:
                if current_position == "BUY":
                    # Long position
                    profit_pct = ((price - entry_price) / entry_price) * 100
                elif current_position == "SELL":
                    # Short position
                    profit_pct = ((entry_price - price) / entry_price) * 100
                
                total_profit += profit_pct
                
                if profit_pct > 0:
                    wins += 1
                else:
                    losses += 1
                
                trades.append({
                    "entry_signal": current_position,
                    "entry_price": float(entry_price),
                    "exit_signal": signal,
                    "exit_price": float(price),
                    "profit_pct": round(profit_pct, 2)
                })
            
            # Mở position mới
            current_position = signal
            entry_price = price
    
    total_trades = len(trades)
    win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
    avg_profit = (total_profit / total_trades) if total_trades > 0 else 0
    
    # Tìm trade tốt nhất và tệ nhất
    best_trade = max(trades, key=lambda x: x['profit_pct']) if trades else None
    worst_trade = min(trades, key=lambda x: x['profit_pct']) if trades else None
    
    return {
        "total_trades": total_trades,
        "wins": wins,
        "losses": losses,
        "win_rate": round(win_rate, 2),
        "total_profit": round(total_profit, 2),
        "avg_profit": round(avg_profit, 2),
        "best_trade": best_trade,
        "worst_trade": worst_trade,
        "trades": trades[-20:]  # 20 trades gần nhất
    }

# ====== BOT LOOP ======
def run_bot():
    global bot_status, signal_history, price_history
    last_signal = None
    last_entry_price = None
    
    print(f"🚀 Bot AlphaTrend đã khởi động!")
    print(f"📈 Symbol: {SYMBOL}")
    print(f"⏱️  Interval: {INTERVAL}")
    print(f"🔄 Kiểm tra mỗi: {CHECK_INTERVAL}s")
    print("-" * 50)
    
    bot_status["status"] = "running"

    while True:
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print(f"⏰ Kiểm tra tín hiệu lúc {timestamp}")
            
            data = get_binance_data(SYMBOL, INTERVAL)
            data = alpha_trend(data, ALPHA_LENGTH, SMOOTH)

            current_trend = data['trend'][-1]
            current_price = float(data['close'][-1])
            
            signal = "BUY" if current_trend == 1 else "SELL" if current_trend == -1 else None
            
            # Lưu giá vào history
            price_history.append({
                "timestamp": timestamp,
                "price": current_price
            })
            if len(price_history) > max_history:
                price_history.pop(0)
            
            # Cập nhật status
            bot_status["last_check"] = timestamp
            bot_status["current_price"] = current_price
            bot_status["status"] = "running"
            
            print(f"📊 Giá hiện tại: ${current_price:,.2f} | Tín hiệu: {signal}")

            if signal and signal != last_signal:
                print(f"🔔 Phát hiện tín hiệu mới: {signal}")
                
                # Tính profit nếu có lệnh trước
                profit = None
                if last_signal and last_entry_price:
                    if last_signal == "BUY":
                        # Đã BUY trước đó, giờ SELL -> tính profit
                        profit = ((current_price - last_entry_price) / last_entry_price) * 100
                    elif last_signal == "SELL":
                        # Đã SELL (short) trước đó, giờ BUY (close short) -> tính profit
                        profit = ((last_entry_price - current_price) / last_entry_price) * 100
                
                # Lưu tín hiệu vào history
                signal_history.append({
                    "timestamp": timestamp,
                    "signal": signal,
                    "price": current_price,
                    "profit": round(profit, 2) if profit is not None else None
                })
                if len(signal_history) > max_history:
                    signal_history.pop(0)
                
                # Gửi Discord alert
                send_discord_alert(signal, current_price)
                
                # Cập nhật last signal
                last_signal = signal
                last_entry_price = current_price
                bot_status["last_signal"] = signal

        except Exception as e:
            print(f"❌ Error in bot loop: {e}")
            bot_status["status"] = f"error: {str(e)}"

        time.sleep(CHECK_INTERVAL)

# ====== MAIN ======
if __name__ == "__main__":
    # Chạy bot trong background thread
    bot_thread = Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Chạy Flask server
    print(f"🌐 Starting web server on port {PORT}")
    app.run(host='0.0.0.0', port=PORT)
