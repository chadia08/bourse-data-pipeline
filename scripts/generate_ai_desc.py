import os
import time
import google.generativeai as genai
from pymongo import MongoClient
from datetime import datetime

# Configuration API
GOOGLE_API_KEY = "AIzaSyAHEAd2MUlBQDkitVTg_0d2EfFt6oAClMY"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# Connexion MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["bourse_cache"]
collection = db["kpi_history"]

def generate_with_retry():
    # On cherche les entreprises sans description
    companies = list(collection.find({"description": {"$exists": False}}))
    print(f"Reste à traiter : {len(companies)} entreprises")

    for i, comp in enumerate(companies):
        ticker = comp.get("Symbole")
        name = comp.get("nom", ticker)
        
        print(f"[{i+1}/{len(companies)}] Génération pour {name}...")
        
        prompt = f"Rédige une description de 2 lignes max en français pour l'entreprise {name} ({ticker})."

        try:
            response = model.generate_content(prompt)
            description = response.text.strip()
            
            collection.update_one(
                {"_id": comp["_id"]},
                {"$set": {"description": description, "last_ai_update": datetime.now()}}
            )
            
            # PAUSE STRATÉGIQUE : 
            # On attend 4 secondes entre chaque requête pour respecter la limite gratuite (15 RPM)
            time.sleep(4) 
            
        except Exception as e:
            if "429" in str(e):
                print("⚠️ Limite atteinte (Rate Limit). Pause de 60 secondes...")
                time.sleep(60) # Grosse pause si l'API nous bloque
            else:
                print(f"❌ Erreur pour {ticker}: {e}")

if __name__ == "__main__":
    generate_with_retry()