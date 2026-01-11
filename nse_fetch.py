import requests

# NSE Session setup karne ke liye function
def get_nse_data(url):
    # 1. Headers set karein (Asli Browser ki tarah)
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
        'accept-language': 'en-US,en;q=0.9',
        'accept-encoding': 'gzip, deflate, br'
    }

    # 2. Ek session banayein (Taki cookies save rahein)
    session = requests.Session()
    
    try:
        # 3. Pehle main page par jayein cookies lene ke liye
        session.get("https://www.nseindia.com", headers=headers, timeout=10)
        
        # 4. Ab asli API data fetch karein
        response = session.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return response.json() # Data mil gaya!
        else:
            print(f"Error! Status Code: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Connection Error: {e}")
        return None

# Aapka main function jo bot call karega
def fetch_option_chain(symbol="NIFTY"):
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
    data = get_nse_data(url)
    return data
