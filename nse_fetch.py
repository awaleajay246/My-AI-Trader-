import requests # 'i' chhota rakhein

# Global session banayein taki baar-baar cookies na leni padein
session = requests.Session()

def get_nse_data(url):
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
        'accept-language': 'en-US,en;q=0.9',
        'accept-encoding': 'gzip, deflate, br'
    }
    
    try:
        # Agar session mein cookies nahi hain, toh pehle home page par jayein
        if not session.cookies:
            session.get("https://www.nseindia.com", headers=headers, timeout=10)
        
        response = session.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 403:
            print("Error: NSE ne IP block kar diya hai (403 Forbidden)")
            return None
        else:
            print(f"Error! Status Code: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Connection Error: {e}")
        return None

def fetch_option_chain(symbol="NIFTY"):
    # LTP Calculator ke liye NIFTY aur BANKNIFTY ka API alag hota hai
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
    return get_nse_data(url)
