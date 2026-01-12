import requests
import time
import random

# Global session taaki cookies bani rahein
session = requests.Session()

def fetch_option_chain(symbol="NIFTY"):
    # Har baar thoda alag user-agent taaki NSE ko shak na ho
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ]

    headers = {
        'user-agent': random.choice(user_agents),
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-US,en;q=0.9,hi;q=0.8',
        'accept-encoding': 'gzip, deflate, br',
        'referer': 'https://www.nseindia.com/get-quotes/derivative?symbol=NIFTY',
        'device-memory': '8'
    }

    try:
        # Step 1: Pehle NSE Home page par jana hi padega (Cookies ke liye)
        print("Connecting to NSE Home...")
        base_url = "https://www.nseindia.com"
        session.get(base_url, headers=headers, timeout=10)
        
        # 3 to 5 second ka random wait (Asli insaan ki tarah)
        time.sleep(random.uniform(3, 5))

        # Step 2: Ab data maangein
        print(f"Requesting Option Chain for {symbol}...")
        api_url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
        response = session.get(api_url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"NSE Rejected: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Network Error: {str(e)}")
        return None
