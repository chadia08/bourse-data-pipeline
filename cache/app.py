import streamlit as st
from pymongo import MongoClient
import pandas as pd
import joblib

# Configuration de la page
st.set_page_config(page_title="Market IA Dashboard", layout="wide")

# 1. Connexion à MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['bourse_cache']
collection = db['market_summary']

# 2. Chargement du modèle IA (Léger) et du Scaler
@st.cache_resource # Pour ne pas recharger le modèle à chaque clic
def load_assets():
    model = joblib.load('modele_bourse_leger.pkl')
    scaler = joblib.load('scaler_bourse.pkl')
    return model, scaler

model, scaler = load_assets()

# --- INTERFACE ---
st.title("📊 Dashboard Boursier Temps Réel & IA")

# Barre latérale pour choisir l'action
all_tickers = collection.distinct("ticker")
selected_ticker = st.sidebar.selectbox("Choisir une action", all_tickers)

# Récupération des données depuis le Cache MongoDB
data = collection.find_one({"ticker": selected_ticker})

if data:
    col1, col2, col3 = st.columns(3)
    col1.metric("Prix Moyen", f"{data['avg_price']} $")
    col2.metric("Plus Haut 24h", f"{data['day_high']} $")
    col3.metric("Volume Total", f"{data['total_volume']:,}")

    st.write(f"Dernière mise à jour : {data['timestamp']}")

    # --- PARTIE PRÉDICTION ---
    st.subheader("🤖 Prédiction IA pour demain")
    
    # Ici, on simule la préparation des données pour le modèle
    # (En situation réelle, on utiliserait les dernières colonnes de ClickHouse)
    st.info(f"Le modèle analyse les tendances pour {selected_ticker}...")
    
    # Bouton pour lancer l'IA
    if st.button("Lancer la prédiction"):
        # Exemple simplifié : on prédit à partir du prix moyen
        # (À adapter avec tes colonnes X_train réelles)
        st.success("Prédiction générée avec succès !")
        # prediction = model.predict(...)