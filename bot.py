import os
import asyncio
from datetime import datetime
import pytz
from telegram import Bot
from nse_fetch import fetch_option_chain
from analyzer import build_report

# Setup
IST = pytz.timezone("Asia/Kolkata")
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
bot = Bot(token=TOKEN)

async def send_msg(text):
    await bot.send_message(chat_id=CHAT_ID, text=text, parse_mode='Markdown')

async def main():
    now = datetime.now(IST)
    
    # Market Hours Check (9:15 AM to 3:30 PM)
    # Testing ke liye aap ise abhi comment out kar sakte hain
    if now.weekday() >= 5: # Saturday/Sunday
        print("Market is Closed today.")
        return

    try:
        # 1. Data Fetch karein
        data = fetch_option_chain("NIFTY")
        if not data: return

        # 2. LTP Analysis (COA 1.0 & 2.0)
        report = build_report(data, "NIFTY", data['records']['underlyingValue'], 50000, "STANDARD")

        # 3. Message Format (Dr. Vinay ji ke style mein)
        msg = (
            f"📊 *LTP CALCULATOR REPORT: {report['symbol']}*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📍 *Spot:* {report['spot']}\n"
            f"🛡️ *Support:* {report['support']}\n"
            f"🚧 *Resistance:* {report['resistance']}\n"
            f"📈 *Scenario:* {report['scenario']}\n"
            f"🌀 *COA 2.0:* {report['coa_2']}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"🎯 *Bias:* {report['bias']}\n"
        )
        
        if report['bias'] != "NEUTRAL":
            msg += (
                f"✅ *Entry:* {report['entry']}\n"
                f"🛑 *SL:* {report['sl']}\n"
                f"🏁 *Target:* {report['target']}\n"
                f"💎 *Trade:* {report['trade_strike']}"
            )
        
        await send_msg(msg)
        print("Report sent to Telegram!")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
