import requests
import time
import random


class NSEFetcher:
    def __init__(self):
        self.session = requests.Session()
        self.max_retries = 5
        self.base_url = "https://www.nseindia.com/api/option-chain-indices?symbol="

        # Default headers (very important)
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "*/*",
            "Connection": "keep-alive",
            "Referer": "https://www.nseindia.com/option-chain",
        }

    def refresh_cookies(self):
        """
        NSE blocks requests without cookies.
        This function gets fresh cookies using the homepage.
        """
        try:
            homepage = "https://www.nseindia.com/"
            self.session.get(homepage, headers=self.headers, timeout=5)
        except Exception:
            pass  # ignore

    def fetch(self, symbol: str):
        """
        Fetch NSE option chain with retries and fallback.
        """
        url = self.base_url + symbol.upper()

        for attempt in range(1, self.max_retries + 1):
            try:
                # Try new cookies every attempt
                self.refresh_cookies()

                response = self.session.get(
                    url,
                    headers=self.headers,
                    timeout=7
                )

                # Cloud servers often show status 200 but empty response
                if response.status_code == 200 and len(response.text) > 200:
                    return response.json()

                print(
                    f"[Attempt {attempt}] Invalid/empty response — "
                    f"Len={len(response.text)}"
                )

            except Exception as e:
                print(f"[Attempt {attempt}] Error: {e}")

            # Random delay: avoids block
            time.sleep(random.uniform(1.2, 2.4))

        raise Exception(
            f"Failed fetching NSE Option Chain for {symbol} after {self.max_retries} retries"
        )


# RUN DIRECTLY (optional test)
if __name__ == "__main__":
    nse = NSEFetcher()
    data = nse.fetch("BANKNIFTY")
    print("SUCCESS ✓")
    print("Keys:", data.keys())
