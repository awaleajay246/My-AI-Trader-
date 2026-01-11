from typing import List, Dict, Tuple

def extract_table(option_json) -> List[Dict]:
    recs = option_json.get("records", {}).get("data", [])
    table = []
    for item in recs:
        strike = item.get("strikePrice")
        ce = item.get("CE") or {}
        pe = item.get("PE") or {}
        table.append({
            "strike": int(strike),
            "CE_OI": int(ce.get("openInterest", 0)),
            "CE_VOL": int(ce.get("totalTradedVolume", 0)),
            "CE_dOI": int(ce.get("changeinOpenInterest", 0)),
            "PE_OI": int(pe.get("openInterest", 0)),
            "PE_VOL": int(pe.get("totalTradedVolume", 0)),
            "PE_dOI": int(pe.get("changeinOpenInterest", 0)),
        })
    return table

def get_sr_state(table: List[Dict], side: str) -> Tuple[int, str, float]:
    """
    Support aur Resistance dhoondne ka logic (Volume aur OI ke basis par)
    """
    vol_key = f"{side}_VOL"
    # 1. Highest Volume waala strike dhoondein
    highest = max(table, key=lambda x: x[vol_key])
    h_strike = highest["strike"]
    h_val = highest[vol_key]
    
    # 2. Second Highest Volume dhoondein (WTT/WTB check karne ke liye)
    others = [x for x in table if x["strike"] != h_strike]
    second = max(others, key=lambda x: x[vol_key])
    s_strike = second["strike"]
    s_val = second[vol_key]
    
    # Weakness percentage (LTP Calculator rule: 75% to 100% is weakness)
    weakness_pct = (s_val / h_val) * 100 if h_val > 0 else 0
    
    state = "STRONG"
    if weakness_pct > 75:
        if s_strike > h_strike:
            state = "WTT" # Weak Towards Top
        else:
            state = "WTB" # Weak Towards Bottom
            
    return h_strike, state, round(weakness_pct, 2)

def get_coa_1_scenario(s_state, r_state) -> int:
    """
    Chart of Accuracy 1.0 ke 9 Scenarios ka table
    """
    if s_state == "STRONG" and r_state == "STRONG": return 1
    if s_state == "STRONG" and r_state == "WTT": return 2
    if s_state == "STRONG" and r_state == "WTB": return 3
    if s_state == "WTT" and r_state == "STRONG": return 4
    if s_state == "WTT" and r_state == "WTT": return 5
    if s_state == "WTB" and r_state == "STRONG": return 6
    if s_state == "WTB" and r_state == "WTB": return 7
    return 0 # Unknown

def get_coa_2_logic(table: List[Dict]) -> str:
    """
    Chart of Accuracy 2.0 (OI Change ka Pressure)
    """
    total_pe_doi = sum(r["PE_dOI"] for r in table)
    total_ce_doi = sum(r["CE_dOI"] for r in table)
    
    if total_pe_doi > total_ce_doi:
        return "BULLISH PRESSURE (PE Writing High)"
    elif total_ce_doi > total_pe_doi:
        return "BEARISH PRESSURE (CE Writing High)"
    return "SIDEWAYS"

def build_report(option_json: dict, symbol: str, spot: float, capital: int, mode: str) -> dict:
    table = extract_table(option_json)
    if not table:
        raise ValueError("Empty data")
        
    atm = min([r["strike"] for r in table], key=lambda x: abs(x-spot))
    
    # COA 1.0 Analysis
    res_strike, res_state, res_pct = get_sr_state(table, "CE")
    sup_strike, sup_state, sup_pct = get_sr_state(table, "PE")
    scenario_1 = get_coa_1_scenario(sup_state, res_state)
    
    # COA 2.0 Analysis
    coa_2_text = get_coa_2_logic(table)
    
    # Trading Bias based on LTP Rules
    bias = "NEUTRAL"
    if scenario_1 in [2, 4, 5]: bias = "BULLISH"
    if scenario_1 in [3, 6, 7]: bias = "BEARISH"
    
    return {
        "symbol": symbol,
        "spot": spot,
        "atm": atm,
        "resistance": f"{res_strike} ({res_state} {res_pct}%)",
        "support": f"{sup_strike} ({sup_state} {sup_pct}%)",
        "scenario_1": scenario_1,
        "coa_2": coa_2_text,
        "bias": bias,
        "confidence": 70 if bias != "NEUTRAL" else 30,
        "entry": sup_strike if bias == "BULLISH" else res_strike, # EOS / EOR concept
        "target": res_strike if bias == "BULLISH" else sup_strike
    }
