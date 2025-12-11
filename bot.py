# bot.py
import os
import json
from datetime import datetime
import pytz
from nse_fetch import fetch_option_chain
from analyzer import build_report
from telegram_send import format_and_send
from telegram_send import bot as tg_bot

TRADE_LOG = "trade_log.json"
IST = pytz.timezone("Asia/Kolkata")
INDICES = os.getenv("INDICES", "NIFTY,BANKNIFTY").split(",")
MODE = os.getenv("MODE", "STANDARD").upper()
CAPITAL = int(os.getenv("CAPITAL", "50000"))
GIT_NAME = os.getenv("GIT_NAME", "bot")
GIT_EMAIL = os.getenv("GIT_EMAIL", "bot@example.com")

def load_log():
    try:
        with open(TRADE_LOG, "r") as f:
            return json.load(f)
    except:
        return {}

def save_log(data):
    with open(TRADE_LOG, "w") as f:
        json.dump(data, f, indent=4)

def record_signal(symbol):
    log = load_log()
    today = datetime.now(IST).strftime("%Y-%m-%d")
    if today not in log:
        log[today] = {"total":0,"profit":0,"loss":0,"details":[]}
    log[today]["total"] += 1
    log[today]["details"].append({"symbol":symbol, "time": datetime.now(IST).strftime("%H:%M")})
    save_log(log)

def maybe_send_open_close_weekly():
    now = datetime.now(IST)
    hh = now.hour; mm = now.minute; wd = now.weekday()
    if hh==9 and mm==15:
        tg_bot.send_message(chat_id=int(os.getenv("CHAT_ID")), text="🟢 Market Opened — Bot Active")
    if hh==15 and mm==30:
        tg_bot.send_message(chat_id=int(os.getenv("CHAT_ID")), text="🔴 Market Closed — Bot Paused for today")
    if wd==5 and hh==18 and mm==0:
        log = load_log()
        lines = ["📊 WEEKLY REPORT\n"]
        if not log:
            lines.append("No trades this week.")
        else:
            for d, info in log.items():
                lines.append(f"{d} — Total:{info.get('total',0)} Profit:{info.get('profit',0)} Loss:{info.get('loss',0)}")
        tg_bot.send_message(chat_id=int(os.getenv("CHAT_ID")), text="\n".join(lines))

def should_take(report):
    if report["trap"][0]:
        return False, "Trap detected"
    conf = report["confidence"]
    if MODE=="SAFE":
        if conf < 80: return False, f"Low conf {conf}"
        if not (report["scenario1"] in [6,7,8] or report["scenario2"] in [1,3]): return False, "Scenarios not strong"
    else:
        if conf < 60: return False, f"Low conf {conf}"
    return True, "OK"

def process_index(sym):
    try:
        data = fetch_option_chain(sym)
        spot = float(data.get("records",{}).get("underlyingValue",0))
        report = build_report(data, sym, spot, CAPITAL, MODE)
        take, reason = should_take(report)
        if take:
            format_and_send(report, MODE)
            record_signal(sym)
        else:
            print(f"No signal for {sym}: {reason}")
    except Exception as e:
        print("Error processing", sym, e)

def main():
    maybe_send_open_close_weekly()
    now = datetime.now(IST)
    if now.weekday() >= 6:
        return
    # run only between 9:05 and 15:45 IST
    if now.hour < 9 or (now.hour==9 and now.minute < 5):
        return
    for sym in INDICES:
        process_index(sym.strip())

if __name__=="__main__":
    main()
