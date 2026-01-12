import requests
import time

# Ek global session banayein
session = requests.Session()

def get_headers():
    return {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'accept-encoding': 'gzip, deflate, br',
        'referer': 'https://www.nseindia.com/get-quotes/derivative?symbol=NIFTY'
    }

def fetch_option_chain(symbol="NIFTY"):
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
    
    try:
        # 1. Pehle home page par ja kar cookies lein (Human behavior)
        print(f"Step 1: Fetching cookies for {symbol}...")
        session.get("https://www.nseindia.com", headers=get_headers(), timeout=10)
        
        # Thoda wait karein (2 seconds) taki NSE ko shak na ho
        time.sleep(2)
        
        # 2. Asli data fetch karein
        print(f"Step 2: Fetching actual data...")
        response = session.get(url, headers=get_headers(), timeout=15)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"NSE Error: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Connection Error: {e}")
        return None
