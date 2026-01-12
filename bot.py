import os
import asyncio
from datetime import datetime
import pytz
from telegram import Bot
from nse_fetch import fetch_option_chain
from analyzer import build_report

# Timezone set karein
IST = pytz.timezone("Asia/Kolkata")
TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
bot = Bot(token=TOKEN)

async def send_debug_msg(text):
    """Telegram par message bhejne ka function"""
    try:
        await bot.send_message(chat_id=CHAT_ID, text=text, parse_mode='Markdown')
    except Exception as e:
        print(f"Telegram Error: {e}")

async def main():
    now = datetime.now(IST)
    print(f"--- Bot Execution Started at {now} ---")
    
    # STEP 1: Telegram check
    await send_debug_msg(f"🔍 *Bot Scan Start:* {now.strftime('%H:%M:%S')}")

    try:
        # STEP 2: NSE Data fetching check
        print("Fetching NSE Data...")
        data = fetch_option_chain("NIFTY")
        
        if not data:
            await send_debug_msg("❌ *Error:* NSE se data nahi mila (Block ya Network issue).")
            return
        
        print("NSE Data received successfully.")
        await send_debug_msg("✅ *NSE Data:* Mil gaya hai.")

        # STEP 3: Analyzer Logic check
        print("Analyzing Data...")
        spot = data.get('records', {}).get('underlyingValue', 0)
        report = build_report(data, "NIFTY", spot, 50000, "STANDARD")
        
        print(f"Analysis Complete. Bias: {report['bias']}")
        
        # STEP 4: Full Report bhejna (Neutral ho tab bhi)
        msg = (
            f"📊 *LTP REPORT: {report['symbol']}*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📍 *Spot:* {report['spot']}\n"
            f"🛡️ *Support:* {report['support']}\n"
            f"🚧 *Resistance:* {report['resistance']}\n"
            f"📈 *Scenario:* {report['scenario']}\n"
            f"🎯 *Bias:* {report['bias']}\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
        )
        
        if report['bias'] != "NEUTRAL":
            msg += f"✅ *Trade Level:* {report['entry']}\n"
        else:
            msg += "⚠️ *Status:* Market Neutral hai, koi trade nahi."

        await send_debug_msg(msg)
        print("Full report sent to Telegram.")

    except Exception as e:
        error_msg = f"❗ *Crash Error:* {str(e)}"
        print(error_msg)
        await send_debug_msg(error_msg)

if __name__ == "__main__":
    asyncio.run(main())
