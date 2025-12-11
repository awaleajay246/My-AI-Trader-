import requests
import time
from requests.exceptions import RequestException

BASE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/option-chain",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
}

NSE_URL = "https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"

def fetch_option_chain(symbol, retries=5):
    url = NSE_URL.format(symbol=symbol)
    session = requests.Session()
    session.headers.update(BASE_HEADERS)

    # Step 1: Get cookies from home page
    try:
        home = session.get("https://www.nseindia.com", timeout=7)
        cookies = home.cookies.get_dict()
        session.cookies.update(cookies)
    except Exception as e:
        print("Cookie fetch failed:", e)

    last_error = None
    for i in range(retries):
        try:
            time.sleep(0.5)
            res = session.get(url, timeout=10)
            if res.status_code == 200:
                data = res.json()
                if "records" in data and data["records"].get("data"):
                    return data
            last_error = f"Empty/invalid response (status {res.status_code})"
        except Exception as e:
            last_error = e
        time.sleep(1.5)

    raise RuntimeError(f"NSE fetch failed for {symbol}: {last_error}")
