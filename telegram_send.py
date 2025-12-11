# telegram_send.py
import os
from telegram import Bot

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
bot = Bot(token=TOKEN)

def format_and_send(report: dict, mode: str):
    lines = []
    lines.append(f"📊 Signal — {report['symbol']}")
    lines.append(f"Mode: {mode} | Bias: {report['bias']} | Confidence: {report['confidence']}%")
    lines.append(f"Spot: {report['spot']} | ATM: {report['atm']}")
    lines.append("")
    lines.append(f"Scenarios: {report['scenario1']} | {report['scenario2']}")
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
    if report['bias']=="BULLISH":
        lines.append(f"📈 Suggestion: BUY (Entry: {report['entry']} SL: {report['sl']} Target: {report['target']})")
    elif report['bias']=="BEARISH":
        lines.append(f"📉 Suggestion: SELL (Entry: {report['entry']} SL: {report['sl']} Target: {report['target']})")
    else:
        lines.append("⏳ Suggestion: No trade (Neutral/Trap)")
    lines.append(f"Lot size (approx): {report['lot_size']} | SL_distance: {report['sl_distance']}")
    lines.append("")
    lines.append("🔁 Bot: OptionChain-C v1")
    text = "\n".join(lines)
    bot.send_message(chat_id=int(CHAT_ID), text=text)
    return text
