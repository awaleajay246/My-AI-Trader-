# telegram_send.py
import os
from telegram import Bot

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
bot = Bot(token=TOKEN)

def format_and_send(report: dict, mode: str):
    lines = []
    lines.append(f"📊 Signal — {report['symbol']}")
    lines.append(f"Mode: {mode}")
    lines.append(f"Bias: {report['bias']} | Confidence: {report['confidence']}%")
    lines.append(f"Spot: {report['spot']} | ATM: {report['atm']}")
    lines.append("")
    lines.append("Scenarios: " + str(report['scenario1']) + " | " + str(report['scenario2']))
    lines.append(report['scenario_text'])
    lines.append("")
    lines.append("Top PE: " + ", ".join([f"{s}:{oi}" for s,oi in report['top_pe']]))
    lines.append("Top CE: " + ", ".join([f"{s}:{oi}" for s,oi in report['top_ce']]))
    lines.append(f"PCR (ATM band): {report['pcr']}")
    if report['weak_top'] or report['weak_bottom']:
        wt = []
        if report['weak_top']: wt.append("Weak→TOP")
        if report['weak_bottom']: wt.append("Weak→BOTTOM")
        lines.append("Weakness: " + ", ".join(wt))
    if report['trap'][0]:
        lines.append("🚨 Trap: " + report['trap'][1])
    lines.append("")
    # Suggestion conservative
    if report['bias']=="BULLISH":
        entry = report['atm'] + 20
        sl = entry - 60
        tgt = entry + 120
        lines.append("📈 Suggestion: BUY on breakout")
        lines.append(f"Entry: Above {entry} | SL: {sl} | Target: {tgt}")
    elif report['bias']=="BEARISH":
        entry = report['atm'] - 20
        sl = entry + 60
        tgt = entry - 120
        lines.append("📉 Suggestion: SELL on breakdown")
        lines.append(f"Entry: Below {entry} | SL: {sl} | Target: {tgt}")
    else:
        lines.append("⏳ Suggestion: No trade (Neutral/Trap)")
    lines.append("")
    lines.append("🔁 Bot: OptionChain-Signal v1")
    text = "\n".join(lines)
    bot.send_message(chat_id=int(CHAT_ID), text=text)
    return text
