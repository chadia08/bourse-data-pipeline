import os
import google.generativeai as genai
from pymongo import MongoClient
from datetime import datetime

# Configuration de ta clé API Gemini
GOOGLE_API_KEY = "AIzaSyDlvZhY72kYcNb9IzbjeYRYaxeCcrXFncg"
genai.configure(api_key=GOOGLE_API_KEY)
# On utilise Gemini 1.5 Flash : rapide et parfait pour des descriptions
model = genai.GenerativeModel('gemini-2.5-flash')

# Connexion à ta base MongoDB
client = MongoClient("mongodb://localhost:27017/")
db = client["bourse_cache"]
collection = db["kpi_history"]

def generate_company_descriptions():
    # On cherche uniquement les entreprises qui n'ont pas encore de champ 'description'
    companies = list(collection.find({"description": {"$exists": False}}))
    
    if not companies:
        print("Toutes les entreprises ont déjà une description.")
        return

    print(f"Extraction des descriptions pour {len(companies)} entreprises...")

    for comp in companies:
        ticker = comp.get("Symbole")
        # On essaie d'être le plus précis possible pour le prompt
        name = comp.get("nom", ticker)
        
        prompt = f"""Tu es un analyste financier expert de la bourse. 
        Rédige une description très concise (2 phrases maximum) en français pour l'entreprise {name} ({ticker}).
        Explique son activité principale de manière professionnelle."""

        try:
            print(f"→ Génération pour {ticker}...")
            response = model.generate_content(prompt)
            description = response.text.strip()
            
            # On enregistre la description dans le document de l'entreprise
            collection.update_one(
                {"_id": comp["_id"]},
                {"$set": {
                    "description": description, 
                    "last_ai_update": datetime.now()
                }}
            )
        except Exception as e:
            print(f"Erreur pour {ticker}: {e}")

if __name__ == "__main__":
    generate_company_descriptions()