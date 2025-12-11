import requests
import time
from requests.exceptions import RequestException

# **FIX 1: X-Requested-With Header Added**
BASE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/option-chain",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "X-Requested-With": "XMLHttpRequest", # CRITICAL FOR NSE API
}

NSE_URL = "https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"

def fetch_option_chain(symbol, retries=5):
    url = NSE_URL.format(symbol=symbol)
    session = requests.Session()
    session.headers.update(BASE_HEADERS)

    # Step 1: Get cookies from home page (Fix 2: Simplified)
    try:
        # Session object cookies को automatically manage करेगा
        session.get("https://www.nseindia.com", timeout=10) 
    except Exception as e:
        # अगर कुकीज़ लेने में भी fail हो तो वहीं raise कर दें
        raise RequestException(f"NSE home page access failed: {e}")

    last_error = None
    for i in range(retries):
        try:
            # Fix 3: Increased initial wait time
            time.sleep(1.0) 
            res = session.get(url, timeout=15) # timeout भी बढ़ा दिया 
            
            if res.status_code == 200:
                data = res.json()
                # NSE कभी-कभी 200 देता है पर data empty होता है
                if data and "records" in data and data["records"].get("data"):
                    return data
            
            # अगर 200 status code मिला पर data नहीं मिला
            last_error = f"Empty/invalid response (status {res.status_code}) - Response Length: {len(res.text)}"
            
        except Exception as e:
            last_error = e
            
        # Fix 3: Increased retry delay
        time.sleep(5.0) 

    raise RuntimeError(f"NSE fetch failed for {symbol} after {retries} retries: {last_error}")

