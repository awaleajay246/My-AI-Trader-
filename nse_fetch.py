# nse_fetch.py
import requests
import time
from requests.exceptions import RequestException

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "en-US,en;q=0.9"
}
NSE_INDEX_ENDPOINT = "https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"

def fetch_option_chain(symbol: str, retries=3, backoff=1.0):
    """
    Fetch option-chain JSON for NIFTY or BANKNIFTY.
    Returns parsed JSON or raises RuntimeError.
    """
    url = NSE_INDEX_ENDPOINT.format(symbol=symbol)
    sess = requests.Session()
    sess.headers.update(HEADERS)
    # initial GET to set cookies
    try:
        sess.get("https://www.nseindia.com", timeout=5)
    except Exception:
        pass
    for i in range(retries):
        try:
            time.sleep(0.5)
            r = sess.get(url, timeout=10)
            r.raise_for_status()
            return r.json()
        except RequestException as e:
            wait = backoff * (2 ** i)
            time.sleep(wait)
            last_exc = e
    raise RuntimeError(f"Failed fetching NSE option chain for {symbol}: {last_exc}")
