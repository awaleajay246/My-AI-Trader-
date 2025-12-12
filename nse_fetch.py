import requests
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/",
    "Connection": "keep-alive"
}

BASE_URL = "https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"

def fetch_option_chain(symbol: str, retries=5, sleep=1.5):
    """Fetch NSE Option Chain with cloud-friendly session handling."""
    session = requests.Session()
    session.headers.update(HEADERS)

    # Preload cookies
    try:
        session.get("https://www.nseindia.com", timeout=10)
    except:
        pass

    url = BASE_URL.format(symbol=symbol)
    last_error = None

    for attempt in range(retries):
        try:
            time.sleep(sleep)
            res = session.get(url, timeout=15)

            if res.status_code != 200:
                last_error = f"Status {res.status_code}"
                continue

            if len(res.text) < 50:
                last_error = f"Empty response (len={len(res.text)})"
                continue

            return res.json()

        except Exception as e:
            last_error = str(e)
            time.sleep(2)

    raise RuntimeError(f"NSE fetch failed for {symbol}: {last_error}")
