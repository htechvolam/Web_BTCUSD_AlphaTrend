# BTC/USDT AlphaTrend Bot

Bot tự động theo dõi tín hiệu AlphaTrend cho BTC/USDT và gửi thông báo qua Discord webhook.

## 🚀 Deploy lên Render

### 1. Tạo Discord Webhook
1. Vào Discord server của bạn
2. Chọn channel → Settings → Integrations → Webhooks
3. Click "New Webhook" → Copy webhook URL

### 2. Deploy trên Render (FREE)
1. Truy cập [render.com](https://render.com) và đăng nhập
2. Click **"New +"** → chọn **"Web Service"**
3. Kết nối với GitHub repository: `htechvolam/Web_BTCUSD_AlphaTrend`
4. Render sẽ tự động phát hiện file `render.yaml` và chọn **Free plan**
5. **Quan trọng**: Thêm environment variable `DISCORD_WEBHOOK_URL`:
   - Trong trang tạo service, scroll xuống phần **Environment Variables**
   - Tìm `DISCORD_WEBHOOK_URL` và paste webhook URL của bạn vào
6. Click **"Create Web Service"**
7. Service sẽ có URL dạng: `https://btcusd-alphatrend-bot.onrender.com`
8. Truy cập URL để xem trạng thái bot

### 3. Environment Variables

| Variable | Mô tả | Giá trị mặc định |
|----------|-------|------------------|
| `DISCORD_WEBHOOK_URL` | ⚠️ **BẮT BUỘC** - Discord webhook URL | - |
| `SYMBOL` | Cặp giao dịch | `BTCUSDT` |
| `INTERVAL` | Khung thời gian | `15m` |
| `CHECK_INTERVAL` | Thời gian kiểm tra (giây) | `60` |
| `ALPHA_LENGTH` | Độ dài AlphaTrend | `14` |
| `SMOOTH` | Hệ số làm mượt | `1` |

### 4. Chỉnh sửa Environment Variables trên Render
1. Vào service dashboard trên Render
2. Click tab **"Environment"**
3. Thêm/sửa các biến môi trường
4. Click **"Save Changes"** → Service sẽ tự động restart

## 📊 Tính năng
- ✅ Theo dõi tín hiệu AlphaTrend trên khung 15 phút
- ✅ Gửi thông báo Discord khi có tín hiệu BUY/SELL
- ✅ Chạy 24/7 trên Render Free tier
- ✅ Tránh spam - chỉ thông báo khi tín hiệu thay đổi
- ✅ **Dashboard web đẹp mắt** với:
  - 📈 **Biểu đồ giá BTC/USDT real-time** (Chart.js)
  - 📊 **Thống kê chi tiết**: Tổng tín hiệu, Win Rate, Buy/Sell count
  - 💰 **Lợi nhuận ước tính** nếu trade theo bot
  - 📜 **Lịch sử tín hiệu** với P/L từng lệnh
  - 🔄 **Auto-refresh** mỗi 30 giây
  - 📱 **Responsive design** - đẹp trên mọi thiết bị

## 🌐 Web Interface & API

### Dashboard
- **`GET /`** - Dashboard web với giao diện đẹp, hiển thị:
  - Biểu đồ giá BTC/USDT
  - Thống kê bot (Win Rate, Total Signals, P/L)
  - Lịch sử tín hiệu chi tiết
  - Trạng thái bot real-time

### API Endpoints

- **`GET /health`** - Health check
  ```json
  {"status": "ok"}
  ```

- **`GET /api/status`** - Trạng thái bot
  ```json
  {
    "status": "running",
    "symbol": "BTCUSDT",
    "interval": "15m",
    "last_check": "2025-10-23 15:30:00",
    "last_signal": "BUY",
    "current_price": 109699.62
  }
  ```

- **`GET /api/history`** - Lịch sử tín hiệu
  ```json
  {
    "signals": [
      {
        "timestamp": "2025-10-23 15:30:00",
        "signal": "BUY",
        "price": 109500.00,
        "profit": null
      },
      {
        "timestamp": "2025-10-23 16:00:00",
        "signal": "SELL",
        "price": 110000.00,
        "profit": 0.46
      }
    ]
  }
  ```

- **`GET /api/chart`** - Dữ liệu chart (50 điểm gần nhất)
  ```json
  {
    "labels": ["2025-10-23 15:00:00", "2025-10-23 15:01:00", ...],
    "prices": [109500.00, 109520.00, ...]
  }
  ```

## 🛠️ Chạy local

```bash
# Tạo virtual environment
python -m venv venv

# Kích hoạt venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate # Linux/Mac

# Cài đặt dependencies
pip install -r requirements.txt

# Chạy bot
python server.py
```

## 📝 License
MIT
