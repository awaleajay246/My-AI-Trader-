def compute_levels(atm: int, sup_strike: int, res_strike: int, bias: str):
    """
    LTP Calculator ke hisaab se Entry, SL aur Target nikalna
    """
    # NIFTY ke liye standard buffer (Dr. Vinay ji ke rules ke mutabiq)
    # EOS = Support - thoda niche, EOR = Resistance + thoda upar
    buffer = 20 
    
    if bias == "BULLISH":
        entry = sup_strike - 5 # EOS Level
        target = res_strike - 5 # EOR se thoda pehle nikalna safe hai
        sl = entry - 25 # Standard 25-30 points SL in NIFTY
        # Kaunsa Strike Price kharidna hai? (Bullish mein ATM ya 1 strike niche ITM)
        suggested_strike = atm - 50 if atm % 50 == 0 else atm
        option_type = "CE"
        
    elif bias == "BEARISH":
        entry = res_strike + 5 # EOR Level
        target = sup_strike + 5 # EOS se thoda pehle nikalna safe hai
        sl = entry + 25
        # Bearish mein ATM ya 1 strike upar ITM
        suggested_strike = atm + 50 if atm % 50 == 0 else atm
        option_type = "PE"
        
    else:
        return None

    return {
        "entry": entry,
        "sl": sl,
        "target": target,
        "trade_strike": f"{suggested_strike} {option_type}"
    }

def build_report(option_json: dict, symbol: str, spot: float, capital: int, mode: str) -> dict:
    table = extract_table(option_json)
    if not table:
        raise ValueError("Empty data")
        
    atm = min([r["strike"] for r in table], key=lambda x: abs(x-spot))
    
    # 1. Support & Resistance State (COA 1.0)
    res_strike, res_state, res_pct = get_sr_state(table, "CE")
    sup_strike, sup_state, sup_pct = get_sr_state(table, "PE")
    scenario_1 = get_coa_1_scenario(sup_state, res_state)
    
    # 2. Market Pressure (COA 2.0)
    coa_2_text = get_coa_2_logic(table)
    
    # 3. Decision Logic
    bias = "NEUTRAL"
    if scenario_1 in [2, 4, 5]: bias = "BULLISH"
    if scenario_1 in [3, 6, 7]: bias = "BEARISH"
    
    # 4. Entry, SL, Target Calculation
    trade_details = compute_levels(atm, sup_strike, res_strike, bias)
    
    report = {
        "symbol": symbol,
        "spot": spot,
        "atm": atm,
        "resistance": f"{res_strike} ({res_state} {res_pct}%)",
        "support": f"{sup_strike} ({sup_state} {sup_pct}%)",
        "scenario": scenario_1,
        "bias": bias,
        "coa_2": coa_2_text
    }
    
    # Agar bias Neutral nahi hai, toh trade details add karein
    if trade_details:
        report.update(trade_details)
        
    return report
