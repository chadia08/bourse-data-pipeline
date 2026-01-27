import requests
import json
import sys
import pandas as pd
import io

def get_securities_direct():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    
    # On ajoute une identité de navigateur pour éviter le 403
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # On télécharge d'abord le contenu avec requests
        response = requests.get(url, headers=headers, timeout=10)
        
        # On donne le texte à Pandas
        tables = pd.read_html(io.StringIO(response.text))
        df = tables[0]
        
        for _, row in df.head(50).iterrows():
            data = {
                "symbol": str(row['Symbol']),
                "company_name": str(row['Security']),
                "sector": str(row['GICS Sector']),
                "updated_at": pd.Timestamp.now().isoformat()
            }
            print(json.dumps(data))
            sys.stdout.flush()
            
    except Exception as e:
        print(f"Erreur fatale : {e}", file=sys.stderr)

if __name__ == "__main__":
    get_securities_direct()