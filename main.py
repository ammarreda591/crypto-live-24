import os
import asyncio
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ضع التوكن الخاص بك هنا من BotFather
TOKEN = "9244909727:AAFlGGgazjVaKMGRFiMZDoxb-yKQE1jLpMQ"

# رابط موقعك على Render
WEBAPP_URL = os.getenv("RENDER_EXTERNAL_URL", "https://crypto-live-24.onrender.com")

app = FastAPI()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Crypto Live 24</title>
    <script src="https://telegram.org/js/telegram-web-app.js"></script>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background-color: #0f172a;
            color: #f8fafc;
            margin: 0;
            padding: 16px;
        }
        .header { text-align: center; margin-bottom: 20px; }
        .header h1 { font-size: 22px; margin: 0 0 5px 0; color: #38bdf8; }
        .search-box {
            width: 100%; padding: 12px; border-radius: 10px;
            border: 1px solid #334155; background: #1e293b; color: white;
            font-size: 14px; margin-bottom: 15px; box-sizing: border-box;
        }
        .card {
            background: #1e293b; border: 1px solid #334155; border-radius: 12px;
            padding: 14px; margin-bottom: 10px; display: flex;
            justify-content: space-between; align-items: center;
        }
        .coin-info h3 { margin: 0; font-size: 16px; }
        .coin-info p { margin: 3px 0 0 0; font-size: 12px; color: #94a3b8; }
        .coin-price { text-align: left; }
        .price-val { font-weight: bold; font-size: 16px; margin: 0; }
        .change { font-size: 12px; margin: 3px 0 0 0; }
        .positive { color: #22c55e; }
        .negative { color: #ef4444; }
        .disclaimer {
            margin-top: 25px; text-align: center; font-size: 11px;
            color: #f59e0b; background: rgba(245, 158, 11, 0.1);
            padding: 10px; border-radius: 8px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>📈 Crypto Live 24</h1>
        <p>أسعار العملات الرقمية المباشرة (عرض فقط)</p>
    </div>
    <input type="text" id="search" class="search-box" placeholder="ابحث عن عملة (مثال: Bitcoin)..." onkeyup="filterCoins()">
    <div id="coins-list">جاري تحميل الأسعار الحية...</div>
    <div class="disclaimer">
        ⚠️ تنبيه: هذا التطبيق مخصص لعرض الأسعار المباشرة فقط ولا يدعم أي بيع أو شراء.
    </div>
    <script>
        window.Telegram.WebApp.ready();
        window.Telegram.WebApp.expand();
        let allCoinsData = [];
        async function fetchPrices() {
            try {
                const res = await fetch('https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=20&page=1&sparkline=false');
                const data = await res.json();
                allCoinsData = data;
                renderCoins(data);
            } catch (e) {
                document.getElementById('coins-list').innerHTML = '<p style="text-align:center; color:red;">خطأ في جلب الأسعار، حاول مرة أخرى.</p>';
            }
        }
        function renderCoins(coins) {
            const container = document.getElementById('coins-list');
            if (!coins || coins.length === 0) {
                container.innerHTML = '<p style="text-align:center;">لا توجد نتائج مطابقة</p>';
                return;
            }
            container.innerHTML = coins.map(coin => {
                const isPos = coin.price_change_percentage_24h >= 0;
                const changeClass = isPos ? 'positive' : 'negative';
                const changeSign = isPos ? '+' : '';
                const price = coin.current_price ? coin.current_price.toLocaleString('en-US', { style: 'currency', currency: 'USD' }) : '$0';
                return `
                    <div class="card">
                        <div class="coin-info">
                            <div style="display:flex; align-items:center; gap:10px;">
                                <img src="${coin.image}" width="28" height="28" style="border-radius:50%;">
                                <div>
                                    <h3>${coin.name}</h3>
                                    <p>${coin.symbol.toUpperCase()}</p>
                                </div>
                            </div>
                        </div>
                        <div class="coin-price">
                            <p class="price-val">${price}</p>
                            <p class="change ${changeClass}">${changeSign}${coin.price_change_percentage_24h ? coin.price_change_percentage_24h.toFixed(2) : 0}%</p>
                        </div>
                    </div>
                `;
            }).join('');
        }
        function filterCoins() {
            const query = document.getElementById('search').value.toLowerCase();
            const filtered = allCoinsData.filter(coin => 
                coin.name.toLowerCase().includes(query) || coin.symbol.toLowerCase().includes(query)
            );
            renderCoins(filtered);
        }
        fetchPrices();
        setInterval(fetchPrices, 15000);
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML_TEMPLATE

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 فتح لوحة أسعار العملات (Mini App)", web_app=WebAppInfo(url=WEBAPP_URL))]
    ])
    await update.message.reply_text(
        "مرحباً بك في بوت **CryptoLive24**! 🪙\n\n"
        "هذا البوت مخصص لعرض أسعار العملات الرقمية مباشرة (لايف) بدون بيع أو شراء.\n\n"
        "اضغط على الزر أدناه لفتح التطبيق التفاعلي:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

@app.on_event("startup")
async def startup_event():
    telegram_app = ApplicationBuilder().token(TOKEN).build()
    telegram_app.add_handler(CommandHandler("start", start))
    await telegram_app.initialize()
    await telegram_app.start()
    await telegram_app.updater.start_polling()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
