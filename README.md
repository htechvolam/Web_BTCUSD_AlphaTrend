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
- ✅ Web interface để kiểm tra trạng thái

## 🌐 API Endpoints

Sau khi deploy, bạn có thể truy cập các endpoint sau:

- **`GET /`** - Trang chủ với thông tin bot và trạng thái hiện tại
  ```json
  {
    "name": "BTC/USDT AlphaTrend Bot",
    "status": "running",
    "symbol": "BTCUSDT",
    "interval": "15m",
    "last_check": "2025-10-23 15:30:00",
    "last_signal": "BUY",
    "current_price": 109699.62
  }
  ```

- **`GET /health`** - Health check endpoint
  ```json
  {"status": "ok"}
  ```

- **`GET /status`** - Chi tiết trạng thái bot
  ```json
  {
    "status": "running",
    "last_check": "2025-10-23 15:30:00",
    "last_signal": "BUY",
    "current_price": 109699.62
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
