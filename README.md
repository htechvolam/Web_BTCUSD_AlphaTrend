# BTC/USDT AlphaTrend Bot

Bot tự động theo dõi tín hiệu AlphaTrend cho BTC/USDT và gửi thông báo qua Discord webhook.

## 🚀 Deploy lên Render

### 1. Tạo Discord Webhook
1. Vào Discord server của bạn
2. Chọn channel → Settings → Integrations → Webhooks
3. Click "New Webhook" → Copy webhook URL

### 2. Deploy trên Render
1. Truy cập [render.com](https://render.com) và đăng nhập
2. Click **"New +"** → chọn **"Background Worker"**
3. Kết nối với GitHub repository: `htechvolam/Web_BTCUSD_AlphaTrend`
4. Render sẽ tự động phát hiện file `render.yaml`
5. **Quan trọng**: Thêm environment variable `DISCORD_WEBHOOK_URL`:
   - Trong trang tạo service, scroll xuống phần **Environment Variables**
   - Tìm `DISCORD_WEBHOOK_URL` và paste webhook URL của bạn vào
6. Click **"Create Background Worker"**

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
- ✅ Chạy 24/7 trên Render (miễn phí)
- ✅ Tránh spam - chỉ thông báo khi tín hiệu thay đổi

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
