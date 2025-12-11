import requests
import time
import json
from requests.exceptions import RequestException

# --- CONFIGURATION ---

# Option Chain API URL
NSE_URL = "https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"

# Headers combining the best of the working bot and Option Chain requirements
BASE_HEADERS = {
    # Working Bot का User-Agent: Often more trusted by NSE than newer ones
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.4896.127 Safari/537.36',
    
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.9',
    
    # Referer set to Equity Derivatives page (from your working bot)
    'Referer': 'https://www.nseindia.com/market-data/equity-derivatives',
    
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    
    # CRITICAL for NSE API calls (Mimics AJAX call from browser)
    "X-Requested-With": "XMLHttpRequest", 
}


# --- FUNCTION TO FETCH DATA ---

def fetch_option_chain(symbol, retries=5):
    """
    Fetches Option Chain data for a given symbol from NSE.
    Uses session handling and retries to bypass security checks.
    """
    url = NSE_URL.format(symbol=symbol)
    session = requests.Session()
    session.headers.update(BASE_HEADERS)

    print(f"--- Starting fetch for {symbol} ---")
    
    # Step 1: Hit NSE Home Page to get necessary session cookies
    try:
        print("Step 1: Fetching initial session cookies...")
        # Timeout बढ़ा दिया
        session.get("https://www.nseindia.com", timeout=15) 
        print("Cookies fetched successfully.")
    except Exception as e:
        # अगर कुकीज़ लेने में ही fail हो जाए तो वहीं error raise कर दें
        raise RequestException(f"NSE home page access failed during cookie fetch: {e}")

    last_error = None
    
    # Step 2: Try fetching Option Chain data multiple times
    for i in range(retries):
        try:
            # Delay added to prevent rate-limiting/suspicion
            time.sleep(2.0) 
            print(f"Attempt {i+1}/{retries}: Requesting data from API...")
            
            # Request timeout बढ़ा दिया
            res = session.get(url, timeout=20) 
            
            # Check Status Code
            if res.status_code == 200:
                data = res.json()
                # Check for actual data (not just an empty 200 response)
                if data and "records" in data and data["records"].get("data"):
                    print(f"Success! Data fetched on attempt {i+1}.")
                    return data
            
            # If 200 but data is empty/invalid
            last_error = f"Empty/invalid response (status {res.status_code}) - Response Length: {len(res.text)}"
            print(f"Attempt {i+1} failed: {last_error}")
            
        except json.JSONDecodeError:
            # Sometimes NSE sends an empty HTML page instead of JSON
            last_error = f"JSON Decode Error - Received non-JSON response (Status {res.status_code})"
            print(f"Attempt {i+1} failed: {last_error}")
        except Exception as e:
            last_error = e
            print(f"Attempt {i+1} failed with exception: {e}")
            
        # Long delay before retrying (To look less like a rapid bot)
        time.sleep(5.0) 

    # If all retries fail, raise a final error
    raise RuntimeError(f"NSE fetch failed for {symbol} after {retries} retries: {last_error}")

# --- EXAMPLE USAGE (For Testing) ---
# try:
#     nifty_data = fetch_option_chain("NIFTY")
#     print("\n--- NIFTY Data Fetch Successful ---")
#     # Process your data here...
# except RuntimeError as e:
#     print(f"\nFATAL ERROR: {e}")
