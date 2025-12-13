import requests

def fetch_option_chain(symbol="NIFTY"):
    if symbol == "NIFTY":
        url = "https://raw.githubusercontent.com/varun-digital/option-chain-data/main/nifty.json"
    else:
        url = "https://raw.githubusercontent.com/varun-digital/option-chain-data/main/banknifty.json"

    return requests.get(url).json()
