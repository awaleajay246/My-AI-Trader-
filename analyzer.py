# analyzer.py
from typing import List, Dict, Tuple
import math

def extract_table(option_json) -> List[Dict]:
    data = option_json.get("records", {}).get("data", [])
    table = []
    for item in data:
        strike = item.get("strikePrice")
        ce = item.get("CE") or {}
        pe = item.get("PE") or {}
        table.append({
            "strike": int(strike),
            "CE_OI": int(ce.get("openInterest", 0)),
            "PE_OI": int(pe.get("openInterest", 0)),
            "CE_dOI": int(ce.get("changeinOpenInterest", 0)),
            "PE_dOI": int(pe.get("changeinOpenInterest", 0)),
        })
    return table

def top_n(table: List[Dict], key: str, n=3):
    return sorted(table, key=lambda r: r.get(key,0), reverse=True)[:n]

def compute_pcr(table: List[Dict], atm: int, band=300):
    pe=0; ce=0
    for r in table:
        if abs(r["strike"]-atm) <= band:
            pe += r["PE_OI"]; ce += r["CE_OI"]
    return round((pe/ce) if ce>0 else float('inf'), 2)

def weakness(table: List[Dict], atm: int):
    strikes = sorted([r["strike"] for r in table])
    d = {r["strike"]: r for r in table}
    if atm not in d:
        atm = min(strikes, key=lambda x: abs(x-atm))
    strikes_sorted = sorted(strikes)
    idx = strikes_sorted.index(atm)
    mid = strikes_sorted[max(0, idx-1): min(len(strikes_sorted), idx+2)]
    above = strikes_sorted[idx+1: idx+4]
    below = strikes_sorted[max(0, idx-3): idx]
    def mean(key, keys):
        vals=[d[k][key] for k in keys if k in d]
        return (sum(vals)/len(vals)) if vals else 0
    ce_mid = mean("CE_OI", mid)
    ce_above = mean("CE_OI", above)
    pe_mid = mean("PE_OI", mid)
    pe_below = mean("PE_OI", below)
    weak_top = ce_mid>0 and (ce_above < 0.7 * ce_mid)
    weak_bottom = pe_mid>0 and (pe_below < 0.7 * pe_mid)
    return bool(weak_top), bool(weak_bottom)

def oi_shift(table: List[Dict]):
    total_pe = sum(r["PE_OI"] for r in table)
    total_ce = sum(r["CE_OI"] for r in table)
    if total_pe==0 or total_ce==0:
        return "neutral"
    pe_com = sum(r["strike"]*r["PE_OI"] for r in table)/total_pe
    ce_com = sum(r["strike"]*r["CE_OI"] for r in table)/total_ce
    if pe_com > ce_com + 5:
        return "bullish_shift"
    if ce_com > pe_com + 5:
        return "bearish_shift"
    return "neutral"

def detect_trap(table: List[Dict], spot: float):
    top_ce = sorted(table, key=lambda x: x["CE_dOI"], reverse=True)[:3]
    top_pe = sorted(table, key=lambda x: x["PE_dOI"], reverse=True)[:3]
    avg_top_ce = sum(r["strike"] for r in top_ce)/len(top_ce) if top_ce else 0
    avg_top_pe = sum(r["strike"] for r in top_pe)/len(top_pe) if top_pe else 0
    if avg_top_ce < spot and sum(r["CE_dOI"] for r in top_ce) > 20000:
        return True, "CE additions below spot → resist trap"
    if avg_top_pe > spot and sum(r["PE_dOI"] for r in top_pe) > 20000:
        return True, "PE additions above spot → support trap"
    return False, ""

def classify_scenarios(table: List[Dict]):
    total_pe = sum(r["PE_OI"] for r in table)
    total_ce = sum(r["CE_OI"] for r in table)
    total_pe_d = sum(r["PE_dOI"] for r in table)
    total_ce_d = sum(r["CE_dOI"] for r in table)
    # Chart 2.0
    if total_pe_d > 0 and total_ce_d < 0:
        sc2 = 1; sc2_text = "PE Add + CE Unwind (Bullish)"
    elif total_ce_d > 0 and total_pe_d < 0:
        sc2 = 2; sc2_text = "CE Add + PE Unwind (Bearish)"
    elif total_ce_d > 0 and total_pe_d > 0:
        sc2 = 3; sc2_text = "Both Addition (Big Move)"
    elif total_ce_d < 0 and total_pe_d < 0:
        sc2 = 4; sc2_text = "Both Unwind (Exhaustion)"
    else:
        sc2 = 5; sc2_text = "Mixed/Neutral"

    # Chart 1.0 via PCR
    pcr = (total_pe/total_ce) if total_ce>0 else 1
    if pcr > 1.2:
        sc1 = 7; sc1_text = "Bullish Build"
    elif pcr < 0.8:
        sc1 = 3; sc1_text = "Bearish Build"
    else:
        sc1 = 5; sc1_text = "Neutral/Sideways"
    return sc1, sc2, f"{sc1_text} | {sc2_text}", round(pcr,2)

def build_report(option_json: dict, symbol: str, spot: float):
    table = extract_table(option_json)
    if not table:
        raise ValueError("Empty option table")
    atm = min([r["strike"] for r in table], key=lambda x: abs(x-spot))
    top_pe = top_n(table, "PE_OI", 3)
    top_ce = top_n(table, "CE_OI", 3)
    pcr = compute_pcr(table, atm)
    weak_top, weak_bottom = weakness(table, atm)
    shift = oi_shift(table)
    trap, trap_reason = detect_trap(table, spot)
    sc1, sc2, sc_text, pcr_full = classify_scenarios(table)
    # bias logic
    pe_total = sum(r["PE_OI"] for r in table)
    ce_total = sum(r["CE_OI"] for r in table)
    bias = "NEUTRAL"
    reasons=[]
    if pe_total > ce_total and sum(r["PE_dOI"] for r in table) > 0 and (sc1 in [6,7,8] or sc2 in [1,3]):
        bias="BULLISH"; reasons.append("PE>CE + PE addition")
    if ce_total > pe_total and sum(r["CE_dOI"] for r in table) > 0 and (sc1 in [2,3,4] or sc2 in [2,3]):
        bias="BEARISH"; reasons.append("CE>PE + CE addition")
    if trap or sc2==5 or sc1==5:
        bias="NEUTRAL"
        if trap: reasons.append("Trap:"+trap_reason)
        else: reasons.append("Mixed/Neutral")
    # confidence (simple)
    confidence = 40
    if bias=="BULLISH":
        confidence = 60 + min(30, int(sum(r["PE_dOI"] for r in table)/10000))
    elif bias=="BEARISH":
        confidence = 60 + min(30, int(sum(r["CE_dOI"] for r in table)/10000))
    else:
        confidence = 35
    return {
        "symbol": symbol,
        "spot": spot,
        "atm": atm,
        "top_pe": [(r["strike"], r["PE_OI"]) for r in top_pe],
        "top_ce": [(r["strike"], r["CE_OI"]) for r in top_ce],
        "pcr": pcr,
        "weak_top": weak_top,
        "weak_bottom": weak_bottom,
        "oi_shift": shift,
        "trap": (trap, trap_reason),
        "scenario1": sc1,
        "scenario2": sc2,
        "scenario_text": sc_text,
        "bias": bias,
        "reasons": reasons,
        "confidence": confidence
    }
