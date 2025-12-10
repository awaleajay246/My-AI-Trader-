import os
from telegram import Bot
from datetime import datetime
import pytz
import json

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
MODE = os.getenv("MODE")
CAPITAL = int(os.getenv("CAPITAL", 50000))

bot = Bot(token=TOKEN)

TRADE_LOG_FILE = "trade_log.json"
IST = pytz.timezone("Asia/Kolkata")

def load_trade_log():
    try:
        with open(TRADE_LOG_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_trade_log(log):
    with open(TRADE_LOG_FILE, "w") as f:
        json.dump(log, f, indent=4)

def market_open():
    msg = "🟢 *Market Opened!* \nYour bot is active."
    bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="Markdown")

def market_close():
    msg = "🔴 *Market Closed!* \nStop trading for today."
    bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode="Markdown")

def send_weekly_report():
    log = load_trade_log()
    report = "📊 *WEEKLY REPORT*\n\n"

    if not log:
        report += "No trades this week."
    else:
        for date, data in log.items():
            report += f"📅 {date}\nTotal: {data['total']} | Profit: {data['profit']} | Loss: {data['loss']}\n\n"

    bot.send_message(chat_id=CHAT_ID, text=report, parse_mode="Markdown")

def main():
    now = datetime.now(IST)
    day = now.weekday()
    hour = now.hour
    minute = now.minute

    # Market OPEN alert
    if hour == 9 and minute == 15:
        market_open()

    # Market CLOSE alert
    if hour == 15 and minute == 30:
        market_close()

    # WEEKLY REPORT (Saturday 6 PM)
    if day == 5 and hour == 18 and minute == 0:
        send_weekly_report()

if __name__ == "__main__":
    main()
