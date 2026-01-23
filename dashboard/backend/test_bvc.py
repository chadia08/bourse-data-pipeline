import BVCscrap
import requests
import urllib3
import ssl

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
original_request = requests.Session.request
def patched_request(self, method, url, *args, **kwargs):
    kwargs['verify'] = False
    return original_request(self, method, url, *args, **kwargs)
requests.Session.request = patched_request


try:
    print("--- Session ---")
    # Usually scraping libraries have a way to list stocks.
    # Looking at pypi description for BVCscrap (from memory/inference):
    # It might just scrape specific pages.
    # Let's try `loadata` with a known symbol 'IAM' or 'ITISSALAT AL-MAGHRIB'
    
    print("Trying loadata IAM...")
    try:
        data = BVCscrap.loadata('IAM') # Ticker often used
        print(data)
    except Exception as e:
        print(f"Error IAM: {e}")

    print("Trying loadata 'Marsa Maroc'...")
    try:
        data = BVCscrap.loadata('Marsa Maroc')
        print(data)
    except Exception as e:
        print(f"Error Marsa: {e}")
        
    print("Trying getIndex...")
    try:
        # It takes no args usually?
        idx = BVCscrap.getIndex()
        print(idx)
    except Exception as e:
        print(f"Index error: {e}")

except Exception as e:
    print(e)
