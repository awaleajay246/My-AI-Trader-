import time
from pnsea import get_option_chain # Grok द्वारा सुझाई गई library

def fetch_option_chain(symbol, retries=5):
    """
    Pnsea library का उपयोग करके NSE data fetch करता है।
    यह internally headers और anti-bot bypass संभालता है।
    """
    print(f"--- Starting fetch for {symbol} using pnsea ---")
    
    last_error = None
    for i in range(retries):
        try:
            # Library direct call
            data = get_option_chain(symbol)
            
            # Check if data is valid
            if data and "records" in data:
                print(f"Success! Data fetched for {symbol} on attempt {i+1}")
                return data
            
            last_error = "Invalid data format received"
        except Exception as e:
            last_error = str(e)
            print(f"Attempt {i+1} failed: {e}")
        
        # Rate limiting से बचने के लिए थोड़ा गैप दें
        time.sleep(3)
    
    raise RuntimeError(f"NSE fetch failed for {symbol} after {retries} retries: {last_error}")
