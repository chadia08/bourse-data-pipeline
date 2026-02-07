from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import clickhouse_connect
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from ml_service import ml_service
import pandas as pd  # ← AJOUTEZ CETTE LIGNE


# Charger les variables d'environnement
load_dotenv()

app = FastAPI(title="Bourse Analytics API - ClickHouse + MongoDB Cache")

# Configuration CORS
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# CONNEXIONS BASES DE DONNÉES
# ============================================================

# ClickHouse
def get_clickhouse_client():
    try:
        client = clickhouse_connect.get_client(
            host=os.getenv("CLICKHOUSE_HOST", "localhost"),
            port=int(os.getenv("CLICKHOUSE_PORT", 8123)),
            username=os.getenv("CLICKHOUSE_USER", "default"),
            password=os.getenv("CLICKHOUSE_PASSWORD", "admin"),
            database=os.getenv("CLICKHOUSE_DB", "bourse")
        )
        return client
    except Exception as e:
        print(f"❌ ERREUR CLICKHOUSE : {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Impossible de se connecter à ClickHouse. Erreur: {str(e)}"
        )

# MongoDB
db = None
try:
    mongo_client = MongoClient(os.getenv("MONGODB_URI", "mongodb://localhost:27017/"))
    db = mongo_client["bourse_cache"]
    print("✅ Connexion MongoDB établie (FastAPI)")
except Exception as e:
    print(f"❌ Erreur MongoDB : {e}")


# ============================================================
# ENDPOINTS EXISTANTS
# ============================================================

@app.get("/")
def read_root():
    return {"status": "online", "source": "ClickHouse + MongoDB Cache"}


@app.get("/api/companies")
def get_companies(sector: str = None, search: str = None):
    """Récupère la liste des sociétés"""
    client = get_clickhouse_client()
    
    query = """
    SELECT 
        c.symbole,
        c.nom,
        c.secteur,
        p.prix_cloture,
        p.variation,
        p.volume
    FROM bourse.company c
    LEFT JOIN (
        SELECT symbole, prix_cloture, variation, volume
        FROM bourse.prices_analytics
        ORDER BY date DESC
        LIMIT 1 BY symbole
    ) p ON c.symbole = p.symbole
    WHERE 1=1
    """
    
    parameters = {}
    
    if sector:
        query += " AND c.secteur = {sector:String}"
        parameters['sector'] = sector
        
    if search:
        query += " AND (c.nom ILIKE {search:String} OR c.symbole ILIKE {search:String})"
        parameters['search'] = f"%{search}%"
    
    query += " ORDER BY c.nom ASC"

    try:
        result = client.query(query, parameters=parameters)
        
        companies = []
        for row in result.result_rows:
            companies.append({
                "symbole": row[0],
                "nom": row[1],
                "secteur": row[2],
                "prix_cloture": row[3] if row[3] is not None else None,
                "variation": row[4] if row[4] is not None else 0,
                "volume": row[5] if row[5] is not None else 0
            })
            
        return companies
        
    except Exception as e:
        print(f"❌ Erreur SQL : {e}")
        raise HTTPException(status_code=500, detail=f"Erreur SQL ClickHouse: {str(e)}")


@app.get("/api/sectors")
def get_sectors():
    """Liste des secteurs"""
    client = get_clickhouse_client()
    query = "SELECT DISTINCT secteur FROM bourse.company ORDER BY secteur"
    try:
        result = client.query(query)
        return [row[0] for row in result.result_rows if row[0]]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================
# ENDPOINTS TRADING
# ============================================================
@app.get("/api/trading/overview")
def get_trading_overview():
    """Vue d'ensemble Trading - VERSION SIMPLIFIÉE"""
    if db is None:
        raise HTTPException(status_code=500, detail="MongoDB non disponible")
    
    try:
        # Récupérer un échantillon pour calculs rapides
        momentum_sample = list(db.kpi_momentum.find({}, {"_id": 0}).limit(100))
        prices_sample = list(db.kpi_prices.find({}, {"_id": 0}).limit(100))
        
        # Compter les signaux directement
        signaux_achat = db.kpi_trading_signals.count_documents({"Signal": "Achat"})
        signaux_vente = db.kpi_trading_signals.count_documents({"Signal": "Vente"})
        
        if not momentum_sample:
            raise HTTPException(status_code=404, detail="Aucune donnée disponible")
        
        # Calculs Python simples
        actions_hausse = sum(1 for m in momentum_sample if m.get('KPI_Momentum', {}).get('Performance_5J_PCT', 0) > 0)
        momentum_marche = round((actions_hausse / len(momentum_sample)) * 100, 2)
        
        vol_moyenne = round(
            sum(p.get('KPI_Prices', {}).get('Volatilite_30J', 0) for p in prices_sample) / len(prices_sample), 4
        ) if prices_sample else 0
        
        rvol_moyen = round(
            sum(m.get('KPI_Momentum', {}).get('Volume_Relatif_RVOL', 0) for m in momentum_sample) / len(momentum_sample), 2
        )
        
        return {
            "momentum_marche": {
                "value": momentum_marche,
                "tendance": "Fort" if momentum_marche > 60 else "Modéré" if momentum_marche > 40 else "Faible"
            },
            "volatilite_moyenne": {
                "value": vol_moyenne,
                "status": "Élevée" if vol_moyenne > 0.03 else "Normale"
            },
            "signaux_actifs": {
                "achat": signaux_achat,
                "vente": signaux_vente,
                "total": signaux_achat + signaux_vente
            },
            "volume_relatif": {
                "value": rvol_moyen,
                "status": "Anormal" if rvol_moyen > 1.5 else "Normal"
            }
        }
        
    except Exception as e:
        print(f"Erreur trading/overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/trading/signals")
def get_trading_signals(signal_type: str = None, min_force: int = 0):
    """Liste des signaux de trading"""
    if db is None:
        raise HTTPException(status_code=500, detail="MongoDB non disponible")
    
    try:
        signals = list(db.kpi_trading_signals.find({}, {"_id": 0}))
        indicators = {i['Symbole']: i for i in db.kpi_trading_indicators.find({}, {"_id": 0})}
        momentum = {m['Symbole']: m for m in db.kpi_momentum.find({}, {"_id": 0})}
        prices = {p['Symbole']: p for p in db.kpi_prices.find({}, {"_id": 0})}
        
        result = []
        for signal in signals:
            symbole = signal.get('Symbole')
            
            if signal_type and signal.get('Signal') != signal_type:
                continue
            
            if signal.get('Force', 0) < min_force:
                continue
            
            ind = indicators.get(symbole, {})
            mom = momentum.get(symbole, {})
            price = prices.get(symbole, {})
            
            result.append({
                "symbole": symbole,
                "signal": signal.get('Signal'),
                "force": signal.get('Force'),
                "confiance": signal.get('Confiance'),
                "raisons": signal.get('Raisons', []),
                "rsi": mom.get('KPI_Momentum', {}).get('RSI_14J', 0),
                "macd": ind.get('MACD', {}).get('Histogram', 0),
                "volume_relatif": mom.get('KPI_Momentum', {}).get('Volume_Relatif_RVOL', 0),
                "prix_actuel": price.get('KPI_Prices', {}).get('Dernier_Prix', 0),
                "variation": price.get('KPI_Prices', {}).get('Variation_PCT', 0),
                "derniere_maj": signal.get('Derniere_MAJ')
            })
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/trading/indicators/{symbole}")
def get_trading_indicators(symbole: str):
    """Indicateurs techniques pour un symbole"""
    if db is None:
        raise HTTPException(status_code=500, detail="MongoDB non disponible")
    
    try:
        symbole = symbole.upper()
        indicators = db.kpi_trading_indicators.find_one({"Symbole": symbole}, {"_id": 0})
        
        if not indicators:
            raise HTTPException(status_code=404, detail=f"Indicateurs introuvables pour {symbole}")
        
        return indicators
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/trading/ohlcv/{symbole}")
def get_ohlcv_data(symbole: str, limit: int = 90):
    """Données OHLCV pour graphique candlestick"""
    if db is None:
        raise HTTPException(status_code=500, detail="MongoDB non disponible")
    
    try:
        symbole = symbole.upper()
        ohlcv_doc = db.kpi_trading_ohlcv.find_one({"Symbole": symbole}, {"_id": 0})
        
        if not ohlcv_doc:
            raise HTTPException(status_code=404, detail=f"Données OHLCV introuvables pour {symbole}")
        
        ohlcv_data = ohlcv_doc.get('OHLCV_Data', [])
        
        return {
            "symbole": symbole,
            "periode": ohlcv_doc.get('Periode'),
            "nb_points": len(ohlcv_data[-limit:]),
            "data": ohlcv_data[-limit:]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/trading/heatmap")
def get_sector_heatmap():
    """Heatmap sectorielle"""
    if db is None:
        raise HTTPException(status_code=500, detail="MongoDB non disponible")
    
    try:
        heatmap_doc = db.kpi_trading_heatmap.find_one({"Type": "Secteurs"}, {"_id": 0})
        
        if not heatmap_doc:
            raise HTTPException(status_code=404, detail="Heatmap introuvable")
        
        return {
            "data": heatmap_doc.get('Data', []),
            "derniere_maj": heatmap_doc.get('Derniere_MAJ')
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/trading/movers")
def get_top_movers():
    """Top hausses et baisses"""
    if db is None:
        raise HTTPException(status_code=500, detail="MongoDB non disponible")
    
    try:
        movers_doc = db.kpi_trading_movers.find_one({"Type": "Top_Movers"}, {"_id": 0})
        
        if not movers_doc:
            raise HTTPException(status_code=404, detail="Top movers introuvables")
        
        return {
            "hausses": movers_doc.get('Top_Hausses', []),
            "baisses": movers_doc.get('Top_Baisses', []),
            "derniere_maj": movers_doc.get('Derniere_MAJ')
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/trading/watchlist")
def get_trading_watchlist():
    """Watchlist combinée pour la table principale"""
    if db is None:
        raise HTTPException(status_code=500, detail="MongoDB non disponible")
    
    try:
        signals = list(db.kpi_trading_signals.find({}, {"_id": 0}))
        indicators = {i['Symbole']: i for i in db.kpi_trading_indicators.find({}, {"_id": 0})}
        momentum = {m['Symbole']: m for m in db.kpi_momentum.find({}, {"_id": 0})}
        prices = {p['Symbole']: p for p in db.kpi_prices.find({}, {"_id": 0})}
        fundamentals = {f['Symbole']: f for f in db.kpi_fundamentals.find({}, {"_id": 0})}
        
        watchlist = []
        for signal in signals:
            symbole = signal.get('Symbole')
            ind = indicators.get(symbole, {})
            mom = momentum.get(symbole, {})
            price = prices.get(symbole, {})
            fund = fundamentals.get(symbole, {})
            
            watchlist.append({
                "symbole": symbole,
                "nom": fund.get('Identity', {}).get('Nom', ''),
                "secteur": fund.get('Identity', {}).get('Secteur', ''),
                "prix": price.get('KPI_Prices', {}).get('Dernier_Prix', 0),
                "variation": price.get('KPI_Prices', {}).get('Variation_PCT', 0),
                "volume_relatif": mom.get('KPI_Momentum', {}).get('Volume_Relatif_RVOL', 0),
                "rsi": mom.get('KPI_Momentum', {}).get('RSI_14J', 0),
                "macd_histogram": ind.get('MACD', {}).get('Histogram', 0),
                "macd_tendance": ind.get('MACD', {}).get('Tendance', ''),
                "bollinger_position": ind.get('Bandes_Bollinger', {}).get('Position', ''),
                "signal": signal.get('Signal'),
                "force": signal.get('Force'),
                "confiance": signal.get('Confiance')
            })
        
        return watchlist
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

# ============================================================
# ENDPOINTS POUR LA PAGE INVESTISSEMENT
# ============================================================

@app.get("/api/investment/overview")
def get_investment_overview():
    """Vue d'ensemble Investissement - VERSION SIMPLIFIÉE"""
    if db is None:
        raise HTTPException(status_code=500, detail="MongoDB non disponible")
    
    try:
        # Échantillons pour calculs rapides
        fundamentals_sample = list(db.kpi_fundamentals.find({}, {"_id": 0}).limit(100))
        investment_sample = list(db.kpi_investment.find({}, {"_id": 0}).limit(100))
        
        if not fundamentals_sample:
            raise HTTPException(status_code=404, detail="Aucune donnée disponible")
        
        # Calculs Python simples
        roe_moyen = sum(
            f.get('KPI_Fundamentals', {}).get('ROE_Decimal', 0) * 100 
            for f in fundamentals_sample
        ) / len(fundamentals_sample)
        
        marge_moyenne = sum(
            f.get('KPI_Fundamentals', {}).get('Marge_Beneficiaire_PCT', 0) 
            for f in fundamentals_sample
        ) / len(fundamentals_sample)
        
        dette_moyenne = sum(
            f.get('KPI_Fundamentals', {}).get('Ratio_Dette_Equity', 0) 
            for f in fundamentals_sample
        ) / len(fundamentals_sample)
        
        cagr_moyen = sum(
            i.get('KPI_Investment', {}).get('CAGR_Annualise_PCT', 0) 
            for i in investment_sample
        ) / len(investment_sample) if investment_sample else 0
        
        score_moyen = sum(
            i.get('KPI_Investment', {}).get('Score_Solidite_Financiere', 0) 
            for i in investment_sample
        ) / len(investment_sample) if investment_sample else 0
        
        div_moyen = sum(
            f.get('KPI_Fundamentals', {}).get('Dividendes', 0) 
            for f in fundamentals_sample
        ) / len(fundamentals_sample)
        
        return {
            "qualite": {
                "roe_moyen": round(roe_moyen, 2),
                "marge_moyenne": round(marge_moyenne, 2),
                "status": "Excellente" if roe_moyen > 20 else "Bonne" if roe_moyen > 15 else "Moyenne"
            },
            "croissance": {
                "cagr_moyen": round(cagr_moyen, 2),
                "status": "Forte" if cagr_moyen > 15 else "Modérée" if cagr_moyen > 5 else "Faible"
            },
            "solidite": {
                "score_moyen": round(score_moyen, 0),
                "dette_moyenne": round(dette_moyenne, 2),
                "status": "Solide" if dette_moyenne < 0.5 else "Modérée" if dette_moyenne < 1 else "Élevée"
            },
            "dividendes": {
                "rendement_moyen": round(div_moyen, 2),
                "status": "Élevé" if div_moyen > 3 else "Moyen" if div_moyen > 2 else "Faible"
            }
        }
        
    except Exception as e:
        print(f"Erreur investment/overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/investment/screener")
def get_investment_screener(
    strategy: str = None,
    min_roe: float = None,
    max_pe: float = None,
    min_div: float = None,
    max_debt: float = None
):
    """
    Screener pour filtrer les actions selon critères fondamentaux
    
    Stratégies pré-configurées :
    - "value": P/E<15, ROE>15%, Dette<0.5
    - "dividend": Div>3%, Payout<60%
    - "growth": CAGR>20%, ROE>15%
    - "quality": Score>80, Dette<0.5
    """
    if db is None:
        raise HTTPException(status_code=500, detail="MongoDB non disponible")
    
    try:
        fundamentals = {f['Symbole']: f for f in db.kpi_fundamentals.find({}, {"_id": 0})}
        investment = {i['Symbole']: i for i in db.kpi_investment.find({}, {"_id": 0})}
        
        result = []
        
        for symbole, fund in fundamentals.items():
            inv = investment.get(symbole, {})
            
            fund_data = fund.get('KPI_Fundamentals', {})
            inv_data = inv.get('KPI_Investment', {})
            
            roe = fund_data.get('ROE_Decimal', 0) * 100
            marge = fund_data.get('Marge_Beneficiaire_PCT', 0)
            dette = fund_data.get('Ratio_Dette_Equity', 0)
            dividendes = fund_data.get('Dividendes', 0)
            cagr = inv_data.get('CAGR_Annualise_PCT', 0)
            score = inv_data.get('Score_Solidite_Financiere', 0)
            
            # Appliquer stratégies pré-configurées
            if strategy == "value":
                if not (roe > 15 and dette < 0.5):
                    continue
            elif strategy == "dividend":
                if not (dividendes > 3):
                    continue
            elif strategy == "growth":
                if not (cagr > 20 and roe > 15):
                    continue
            elif strategy == "quality":
                if not (score > 80 and dette < 0.5):
                    continue
            
            # Appliquer filtres personnalisés
            if min_roe and roe < min_roe:
                continue
            if max_debt and dette > max_debt:
                continue
            if min_div and dividendes < min_div:
                continue
            
            result.append({
                "symbole": symbole,
                "nom": fund.get('Identity', {}).get('Nom', ''),
                "secteur": fund.get('Identity', {}).get('Secteur', ''),
                "roe": round(roe, 2),
                "marge": round(marge, 2),
                "dette": round(dette, 2),
                "dividendes": round(dividendes, 2),
                "cagr": round(cagr, 2),
                "score": int(score)
            })
        
        # Trier par score
        result.sort(key=lambda x: x['score'], reverse=True)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/investment/fundamentals/{symbole}")
def get_investment_fundamentals(symbole: str):
    """
    Récupère toutes les données fondamentales pour un symbole :
    - Valorisation (P/E, P/B, etc.)
    - Rentabilité (ROE, ROA, marges)
    - Croissance (CAGR, évolution CA)
    - Solidité (dette, liquidité)
    - Dividendes
    """
    if db is None:
        raise HTTPException(status_code=500, detail="MongoDB non disponible")
    
    try:
        symbole = symbole.upper()
        
        fund = db.kpi_fundamentals.find_one({"Symbole": symbole}, {"_id": 0})
        inv = db.kpi_investment.find_one({"Symbole": symbole}, {"_id": 0})
        
        if not fund:
            raise HTTPException(status_code=404, detail=f"Données introuvables pour {symbole}")
        
        fund_data = fund.get('KPI_Fundamentals', {})
        inv_data = inv.get('KPI_Investment', {}) if inv else {}
        
        return {
            "symbole": symbole,
            "nom": fund.get('Identity', {}).get('Nom', ''),
            "secteur": fund.get('Identity', {}).get('Secteur', ''),
            "rentabilite": {
                "roe": round(fund_data.get('ROE_Decimal', 0) * 100, 2),
                "marge_nette": round(fund_data.get('Marge_Beneficiaire_PCT', 0), 2),
                "eps": round(fund_data.get('EPS', 0), 2)
            },
            "solidite": {
                "ratio_dette": round(fund_data.get('Ratio_Dette_Equity', 0), 2),
                "ratio_courant": round(fund_data.get('Ratio_Courant', 0), 2),
                "score": int(inv_data.get('Score_Solidite_Financiere', 0))
            },
            "croissance": {
                "cagr": round(inv_data.get('CAGR_Annualise_PCT', 0), 2),
                "chiffre_affaires": round(fund_data.get('Chiffre_Affaires', 0), 2)
            },
            "dividendes": {
                "rendement": round(fund_data.get('Dividendes', 0), 2)
            },
            "risque": {
                "volatilite": round(inv_data.get('Volatilite_Annualisee_PCT', 0), 2),
                "max_drawdown": round(inv_data.get('Max_Drawdown_Historique_PCT', 0), 2)
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/investment/watchlist")
def get_investment_watchlist():
    """
    Liste complète pour la page investissement avec tous les indicateurs
    """
    if db is None:
        raise HTTPException(status_code=500, detail="MongoDB non disponible")
    
    try:
        fundamentals = list(db.kpi_fundamentals.find({}, {"_id": 0}))
        investment = {i['Symbole']: i for i in db.kpi_investment.find({}, {"_id": 0})}
        prices = {p['Symbole']: p for p in db.kpi_prices.find({}, {"_id": 0})}
        
        watchlist = []
        for fund in fundamentals:
            symbole = fund.get('Symbole')
            inv = investment.get(symbole, {})
            price = prices.get(symbole, {})
            
            fund_data = fund.get('KPI_Fundamentals', {})
            inv_data = inv.get('KPI_Investment', {})
            price_data = price.get('KPI_Prices', {})
            
            watchlist.append({
                "symbole": symbole,
                "nom": fund.get('Identity', {}).get('Nom', ''),
                "secteur": fund.get('Identity', {}).get('Secteur', ''),
                "prix": round(price_data.get('Dernier_Prix', 0), 2),
                "roe": round(fund_data.get('ROE_Decimal', 0) * 100, 2),
                "marge": round(fund_data.get('Marge_Beneficiaire_PCT', 0), 2),
                "dette": round(fund_data.get('Ratio_Dette_Equity', 0), 2),
                "dividendes": round(fund_data.get('Dividendes', 0), 2),
                "cagr": round(inv_data.get('CAGR_Annualise_PCT', 0), 2),
                "score": int(inv_data.get('Score_Solidite_Financiere', 0))
            })
        
        # Trier par score
        watchlist.sort(key=lambda x: x['score'], reverse=True)
        
        return watchlist
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))




# ============================================================
# ENDPOINTS POUR LA PAGE PRÉDICTIONS ML
# ============================================================

@app.get("/api/predictions/overview")
def get_predictions_overview():
    """Vue d'ensemble Prédictions"""
    if db is None:
        raise HTTPException(status_code=500, detail="MongoDB non disponible")
    
    try:
        total_actions = db.kpi_prices.count_documents({})
        
        return {
            "actions_disponibles": total_actions,
            "modele": "Prophet (Facebook)",
            "type": "Séries temporelles",
            "horizon": "30 jours",
            "status": "Actif" if ml_service.model_loaded else "Inactif"
        }
    except Exception as e:
        print(f"Erreur: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/predictions/history/{symbole}")
def get_prediction_history(symbole: str, days: int = 90):
    """
    Récupère l'historique réel pour afficher avec les prédictions
    """
    try:
        symbole = symbole.upper()
        client = get_clickhouse_client()
        
        query = f"""
        SELECT 
            toString(date) as date,
            prix_cloture as price
        FROM bourse.prices
        WHERE symbole = '{symbole}'
        ORDER BY date DESC
        LIMIT {days}
        """
        
        df = client.query_df(query)
        
        if df.empty:
            raise HTTPException(status_code=404, detail=f"Aucune donnée pour {symbole}")
        
        # Inverser pour avoir l'ordre chronologique
        df = df.iloc[::-1]
        
        history = []
        for _, row in df.iterrows():
            history.append({
                "date": str(row['date']),
                "price": float(row['price'])
            })
        
        return {
            "symbole": symbole,
            "history": history
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/predictions/forecast/{symbole}")
def get_forecast(symbole: str, periods: int = 30):
    """
    Génère des prédictions pour un symbole
    """
    try:
        symbole = symbole.upper()
        
        # Vérifier que le modèle est chargé
        if not ml_service.model:
            raise HTTPException(status_code=500, detail="Modèle ML non disponible")
        
        # Récupérer les données historiques depuis ClickHouse
        client = get_clickhouse_client()
        
        query = f"""
        SELECT 
            date as ds,
            prix_cloture as y
        FROM bourse.prices
        WHERE symbole = '{symbole}'
        ORDER BY date ASC
        """
        
        df = client.query_df(query)
        
        if df.empty:
            raise HTTPException(status_code=404, detail=f"Aucune donnée pour {symbole}")
        
        # Entraîner un modèle spécifique pour ce symbole
        # Note : En production, vous voudriez avoir un modèle par symbole pré-entraîné
        from prophet import Prophet
        
        model = Prophet(
            daily_seasonality=False,
            yearly_seasonality=True,
            weekly_seasonality=True
        )
        
        model.fit(df)
        
        # Créer les dates futures
        future = model.make_future_dataframe(periods=periods)
        forecast = model.predict(future)
        
        # Extraire les prédictions futures uniquement
        predictions = forecast.tail(periods)
        
        result = []
        for _, row in predictions.iterrows():
            result.append({
                "date": row['ds'].strftime('%Y-%m-%d'),
                "predicted_price": round(float(row['yhat']), 2),
                "lower_bound": round(float(row['yhat_lower']), 2),
                "upper_bound": round(float(row['yhat_upper']), 2)
            })
        
        # Calculer la tendance
        first_pred = result[0]['predicted_price']
        last_pred = result[-1]['predicted_price']
        variation_pct = ((last_pred - first_pred) / first_pred) * 100
        
        return {
            "symbole": symbole,
            "horizon": periods,
            "predictions": result,
            "tendance": {
                "direction": "Haussière" if variation_pct > 0 else "Baissière",
                "variation_pct": round(variation_pct, 2),
                "prix_initial": round(first_pred, 2),
                "prix_final": round(last_pred, 2)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/predictions/list")
def get_predictions_list():
    """Liste des symboles disponibles pour prédictions - VERSION RAPIDE"""
    if db is None:
        raise HTTPException(status_code=500, detail="MongoDB non disponible")
    
    try:
        # Utiliser MongoDB au lieu de ClickHouse
        fundamentals = list(db.kpi_fundamentals.find(
            {}, 
            {
                "_id": 0, 
                "Symbole": 1, 
                "Identity.Nom": 1, 
                "Identity.Secteur": 1
            }
        ))
        
        prices = {
            p['Symbole']: p.get('KPI_Prices', {}).get('Dernier_Prix', 0)
            for p in db.kpi_prices.find({}, {"_id": 0, "Symbole": 1, "KPI_Prices.Dernier_Prix": 1})
        }
        
        result = []
        for fund in fundamentals:
            symbole = fund.get('Symbole')
            result.append({
                "symbole": symbole,
                "nom": fund.get('Identity', {}).get('Nom', ''),
                "secteur": fund.get('Identity', {}).get('Secteur', ''),
                "nb_points": 1700,  # Valeur par défaut (données historiques)
                "dernier_prix": prices.get(symbole, 0)
            })
        
        # Trier par nom
        result.sort(key=lambda x: x['nom'])
        
        return result
        
    except Exception as e:
        print(f"Erreur predictions/list: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    """
    Liste des symboles disponibles pour prédictions
    """
    try:
        client = get_clickhouse_client()
        
        query = """
        SELECT 
            c.symbole,
            c.nom,
            c.secteur,
            count(*) as nb_points,
            argMax(p.prix_cloture, p.date) as dernier_prix
        FROM bourse.prices p
        LEFT JOIN bourse.company c ON p.symbole = c.symbole
        GROUP BY c.symbole, c.nom, c.secteur
        HAVING nb_points > 365
        ORDER BY c.nom
        """
        
        df = client.query_df(query)
        
        result = []
        for _, row in df.iterrows():
            result.append({
                "symbole": row['symbole'],
                "nom": row['nom'],
                "secteur": row['secteur'],
                "nb_points": int(row['nb_points']),
                "dernier_prix": float(row['dernier_prix']) if pd.notnull(row['dernier_prix']) else 0
            })
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))