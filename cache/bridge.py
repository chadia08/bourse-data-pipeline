import time
import pandas as pd
import numpy as np
from clickhouse_connect import get_client
from pymongo import MongoClient
from datetime import datetime

# ============================================================
# CONFIGURATION
# ============================================================

try:
    ch_client = get_client(host='localhost', username='default', password='admin', port=8123)
    mongo_client = MongoClient("mongodb://localhost:27017/")
    db = mongo_client["bourse_cache"]
    print("✅ Connexion ClickHouse & MongoDB établie.")
except Exception as e:
    print(f"❌ Erreur de connexion : {e}")
    exit()


# ============================================================
# FONCTIONS POUR LA PAGE TRADING
# ============================================================

# --- 1. INDICATEURS TECHNIQUES ---
def sync_trading_indicators():
    """
    Calcule les indicateurs techniques essentiels :
    - MACD (12, 26, 9)
    - Moyennes Mobiles (MA20, MA50, MA200)
    - Bandes de Bollinger (20 jours, 2 écarts-types)
    - ATR (Average True Range 14)
    - Stochastique (K, D)
    """
    query = """
    WITH 
    ema_data AS (
        SELECT 
            symbole,
            date,
            prix_cloture,
            prix_haut,
            prix_bas,
            avg(prix_cloture) OVER (PARTITION BY symbole ORDER BY date ROWS BETWEEN 11 PRECEDING AND CURRENT ROW) as ema_12,
            avg(prix_cloture) OVER (PARTITION BY symbole ORDER BY date ROWS BETWEEN 25 PRECEDING AND CURRENT ROW) as ema_26,
            avg(prix_cloture) OVER (PARTITION BY symbole ORDER BY date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) as ma_20,
            avg(prix_cloture) OVER (PARTITION BY symbole ORDER BY date ROWS BETWEEN 49 PRECEDING AND CURRENT ROW) as ma_50,
            avg(prix_cloture) OVER (PARTITION BY symbole ORDER BY date ROWS BETWEEN 199 PRECEDING AND CURRENT ROW) as ma_200,
            stddevPop(prix_cloture) OVER (PARTITION BY symbole ORDER BY date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) as std_20,
            greatest(
                prix_haut - prix_bas,
                abs(prix_haut - lagInFrame(prix_cloture, 1) OVER (PARTITION BY symbole ORDER BY date)),
                abs(prix_bas - lagInFrame(prix_cloture, 1) OVER (PARTITION BY symbole ORDER BY date))
            ) as true_range
        FROM bourse.prices
    ),
    macd_calc AS (
        SELECT 
            symbole,
            date,
            prix_cloture,
            ema_12,
            ema_26,
            ma_20,
            ma_50,
            ma_200,
            std_20,
            true_range,
            ema_12 - ema_26 as macd_line,
            avg(ema_12 - ema_26) OVER (PARTITION BY symbole ORDER BY date ROWS BETWEEN 8 PRECEDING AND CURRENT ROW) as signal_line,
            ma_20 + (2 * std_20) as bollinger_upper,
            ma_20 - (2 * std_20) as bollinger_lower,
            avg(true_range) OVER (PARTITION BY symbole ORDER BY date ROWS BETWEEN 13 PRECEDING AND CURRENT ROW) as atr_14
        FROM ema_data
    ),
    stochastic_calc AS (
        SELECT
            symbole,
            date,
            prix_cloture,
            prix_haut,
            prix_bas,
            ((prix_cloture - min(prix_bas) OVER (PARTITION BY symbole ORDER BY date ROWS BETWEEN 13 PRECEDING AND CURRENT ROW)) /
             nullIf(max(prix_haut) OVER (PARTITION BY symbole ORDER BY date ROWS BETWEEN 13 PRECEDING AND CURRENT ROW) - 
                    min(prix_bas) OVER (PARTITION BY symbole ORDER BY date ROWS BETWEEN 13 PRECEDING AND CURRENT ROW), 0)) * 100 as stoch_k
        FROM bourse.prices
    )
    SELECT 
        m.symbole,
        round(m.macd_line, 4) as macd,
        round(m.signal_line, 4) as macd_signal,
        round(m.macd_line - m.signal_line, 4) as macd_histogram,
        round(m.ma_20, 2) as ma_20,
        round(m.ma_50, 2) as ma_50,
        round(m.ma_200, 2) as ma_200,
        round(m.bollinger_upper, 2) as bollinger_upper,
        round(m.ma_20, 2) as bollinger_middle,
        round(m.bollinger_lower, 2) as bollinger_lower,
        round(m.atr_14, 4) as atr,
        round(s.stoch_k, 2) as stochastic_k,
        round(avg(s.stoch_k) OVER (PARTITION BY s.symbole ORDER BY s.date ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 2) as stochastic_d,
        m.prix_cloture as prix_actuel
    FROM macd_calc m
    LEFT JOIN stochastic_calc s ON m.symbole = s.symbole AND m.date = s.date
    WHERE m.date = (SELECT max(date) FROM bourse.prices)
    """
    
    try:
        df = ch_client.query_df(query).fillna(0)
        
        for _, row in df.iterrows():
            db.kpi_trading_indicators.update_one(
                {"Symbole": row['symbole']},
                {"$set": {
                    "MACD": {
                        "MACD_Line": float(row['macd']),
                        "Signal_Line": float(row['macd_signal']),
                        "Histogram": float(row['macd_histogram']),
                        "Tendance": "Haussier" if row['macd'] > row['macd_signal'] else "Baissier"
                    },
                    "Moyennes_Mobiles": {
                        "MA_20": float(row['ma_20']),
                        "MA_50": float(row['ma_50']),
                        "MA_200": float(row['ma_200']),
                        "Prix_Actuel": float(row['prix_actuel']),
                        "Position_MA20": "Au-dessus" if row['prix_actuel'] > row['ma_20'] else "En-dessous",
                        "Golden_Cross": bool(row['ma_50'] > row['ma_200'])
                    },
                    "Bandes_Bollinger": {
                        "Upper": float(row['bollinger_upper']),
                        "Middle": float(row['bollinger_middle']),
                        "Lower": float(row['bollinger_lower']),
                        "Position": "Suracheté" if row['prix_actuel'] > row['bollinger_upper'] 
                                   else "Survendu" if row['prix_actuel'] < row['bollinger_lower'] 
                                   else "Neutre"
                    },
                    "Volatilite": {
                        "ATR_14": float(row['atr'])
                    },
                    "Stochastique": {
                        "K": float(row['stochastic_k']),
                        "D": float(row['stochastic_d']),
                        "Signal": "Suracheté" if row['stochastic_k'] > 80 
                                 else "Survendu" if row['stochastic_k'] < 20 
                                 else "Neutre"
                    },
                    "Derniere_MAJ": datetime.now()
                }}, upsert=True)
        
        print(f"✅ Indicateurs techniques: {len(df)} symboles")
        
    except Exception as e:
        print(f"❌ Erreur sync_trading_indicators: {e}")
        import traceback
        traceback.print_exc()


# --- 2. SIGNAUX DE TRADING ---
def sync_trading_signals():
    """
    Génère des signaux d'achat/vente basés sur :
    - RSI, MACD, Bollinger, Stochastique, Volume
    """
    try:
        indicators = list(db.kpi_trading_indicators.find())
        momentum = list(db.kpi_momentum.find())
        prices = list(db.kpi_prices.find())
        
        signals_count = 0
        
        for ind in indicators:
            symbole = ind['Symbole']
            
            mom = next((m for m in momentum if m['Symbole'] == symbole), None)
            price = next((p for p in prices if p['Symbole'] == symbole), None)
            
            if not mom or not price:
                continue
            
            rsi = mom['KPI_Momentum']['RSI_14J']
            rvol = mom['KPI_Momentum']['Volume_Relatif_RVOL']
            
            macd = ind['MACD']['MACD_Line']
            signal_line = ind['MACD']['Signal_Line']
            prix_actuel = ind['Moyennes_Mobiles']['Prix_Actuel']
            bb_upper = ind['Bandes_Bollinger']['Upper']
            bb_lower = ind['Bandes_Bollinger']['Lower']
            stoch_k = ind['Stochastique']['K']
            
            # Signaux ACHAT
            force_achat = 0
            raisons_achat = []
            
            if rsi < 30:
                force_achat += 1
                raisons_achat.append("RSI survendu (<30)")
            
            if macd > signal_line and macd > 0:
                force_achat += 1
                raisons_achat.append("MACD croisement haussier")
            
            if prix_actuel < bb_lower:
                force_achat += 1
                raisons_achat.append("Prix zone basse Bollinger")
            
            if stoch_k < 20:
                force_achat += 1
                raisons_achat.append("Stochastique survendu")
            
            if rvol > 1.5:
                force_achat += 1
                raisons_achat.append("Volume élevé")
            
            # Signaux VENTE
            force_vente = 0
            raisons_vente = []
            
            if rsi > 70:
                force_vente += 1
                raisons_vente.append("RSI suracheté (>70)")
            
            if macd < signal_line and macd < 0:
                force_vente += 1
                raisons_vente.append("MACD croisement baissier")
            
            if prix_actuel > bb_upper:
                force_vente += 1
                raisons_vente.append("Prix zone haute Bollinger")
            
            if stoch_k > 80:
                force_vente += 1
                raisons_vente.append("Stochastique suracheté")
            
            # Déterminer le signal final
            if force_achat >= 3:
                signal = "Achat"
                force = force_achat
                raisons = raisons_achat
            elif force_vente >= 3:
                signal = "Vente"
                force = force_vente
                raisons = raisons_vente
            else:
                signal = "Neutre"
                force = max(force_achat, force_vente)
                raisons = raisons_achat if force_achat > force_vente else raisons_vente
            
            db.kpi_trading_signals.update_one(
                {"Symbole": symbole},
                {"$set": {
                    "Signal": signal,
                    "Force": min(force, 5),
                    "Raisons": raisons,
                    "Confiance": "Élevée" if force >= 4 else "Moyenne" if force >= 2 else "Faible",
                    "Derniere_MAJ": datetime.now()
                }}, upsert=True)
            
            signals_count += 1
        
        print(f"✅ Signaux de trading: {signals_count} symboles")
        
    except Exception as e:
        print(f"❌ Erreur sync_trading_signals: {e}")
        import traceback
        traceback.print_exc()


# --- 3. DONNÉES HISTORIQUES OHLCV ---
def sync_ohlcv_history(symbole=None, days=None):
    """
    Exporte les données OHLCV pour graphiques candlestick
    Si days=None, charge toutes les données
    """
    try:
        # Détecter la plage de dates réelle
        date_range_query = """
        SELECT min(date) as min_date, max(date) as max_date, count(*) as total
        FROM bourse.prices
        """
        date_result = ch_client.query(date_range_query)
        
        if not date_result.result_rows:
            print("❌ Impossible de récupérer les dates")
            return
        
        min_date, max_date, total_rows = date_result.result_rows[0]
        
        if total_rows == 0:
            print("❌ Table bourse.prices vide")
            return
        
        # Construire la requête
        if days is None:
            where_clause = ""
            print(f"📊 Chargement de TOUTES les données ({min_date} à {max_date})")
        else:
            where_clause = f"WHERE date >= toDate('{max_date}') - {days}"
            print(f"📊 Chargement des {days} derniers jours")
        
        if symbole:
            where_clause += f" {'AND' if where_clause else 'WHERE'} symbole = '{symbole}'"
        
        query = f"""
        SELECT 
            symbole,
            toString(date) as date_str,
            prix_ouverture as open,
            prix_haut as high,
            prix_bas as low,
            prix_cloture as close,
            volume,
            variation
        FROM bourse.prices
        {where_clause}
        ORDER BY symbole, date ASC
        """
        
        df = ch_client.query_df(query)
        
        if df.empty:
            print("⚠️ Aucune donnée retournée")
            return
        
        df.columns = df.columns.str.lower()
        
        symboles_traites = 0
        total_points = 0
        
        for symbole_name, group in df.groupby('symbole'):
            ohlcv_data = []
            for _, row in group.iterrows():
                ohlcv_data.append({
                    "date": str(row['date_str']),
                    "open": float(row['open']) if pd.notnull(row['open']) else 0,
                    "high": float(row['high']) if pd.notnull(row['high']) else 0,
                    "low": float(row['low']) if pd.notnull(row['low']) else 0,
                    "close": float(row['close']) if pd.notnull(row['close']) else 0,
                    "volume": int(row['volume']) if pd.notnull(row['volume']) else 0,
                    "variation": float(row['variation']) if pd.notnull(row['variation']) else 0
                })
            
            db.kpi_trading_ohlcv.update_one(
                {"Symbole": symbole_name},
                {"$set": {
                    "OHLCV_Data": ohlcv_data,
                    "Periode": f"{min_date} à {max_date}",
                    "Nb_Points": len(ohlcv_data),
                    "Derniere_MAJ": datetime.now()
                }}, upsert=True)
            
            symboles_traites += 1
            total_points += len(ohlcv_data)
        
        print(f"✅ OHLCV: {symboles_traites} symboles, {total_points} points")
        
    except Exception as e:
        print(f"❌ Erreur sync_ohlcv_history: {e}")
        import traceback
        traceback.print_exc()


# --- 4. HEATMAP SECTORIELLE ---
def sync_sector_heatmap():
    """Calcule la performance par secteur"""
    try:
        query = """
        SELECT 
            c.secteur,
            count(DISTINCT p.symbole) as nb_actions,
            round(avg(p.variation), 2) as variation_moyenne,
            sum(p.dollar_volume) as volume_total,
            countIf(p.variation > 0) as nb_hausse,
            countIf(p.variation < 0) as nb_baisse
        FROM bourse.prices p
        LEFT JOIN bourse.company c ON p.symbole = c.symbole
        WHERE p.date = (SELECT max(date) FROM bourse.prices)
        GROUP BY c.secteur
        ORDER BY variation_moyenne DESC
        """
        
        df = ch_client.query_df(query)
        
        heatmap_data = []
        for _, row in df.iterrows():
            if pd.isnull(row['secteur']):
                continue
            
            heatmap_data.append({
                "Secteur": row['secteur'],
                "Nb_Actions": int(row['nb_actions']),
                "Variation_Moyenne_PCT": float(row['variation_moyenne']),
                "Volume_Total": float(row['volume_total']),
                "Actions_Hausse": int(row['nb_hausse']),
                "Actions_Baisse": int(row['nb_baisse']),
                "Sentiment": "Positif" if row['variation_moyenne'] > 0.5 
                            else "Négatif" if row['variation_moyenne'] < -0.5 
                            else "Neutre"
            })
        
        db.kpi_trading_heatmap.update_one(
            {"Type": "Secteurs"},
            {"$set": {
                "Data": heatmap_data,
                "Derniere_MAJ": datetime.now()
            }}, upsert=True)
        
        print(f"✅ Heatmap: {len(heatmap_data)} secteurs")
        
    except Exception as e:
        print(f"❌ Erreur sync_sector_heatmap: {e}")


# --- 5. TOP MOVERS ---
def sync_top_movers(top_n=10):
    """Identifie les plus fortes hausses et baisses"""
    try:
        query_hausse = f"""
        SELECT symbole, prix_cloture, variation, volume
        FROM bourse.prices
        WHERE date = (SELECT max(date) FROM bourse.prices)
        ORDER BY variation DESC
        LIMIT {top_n}
        """
        
        query_baisse = f"""
        SELECT symbole, prix_cloture, variation, volume
        FROM bourse.prices
        WHERE date = (SELECT max(date) FROM bourse.prices)
        ORDER BY variation ASC
        LIMIT {top_n}
        """
        
        df_hausse = ch_client.query_df(query_hausse)
        df_baisse = ch_client.query_df(query_baisse)
        
        hausses = [
            {
                "Symbole": row['symbole'],
                "Prix": float(row['prix_cloture']),
                "Variation_PCT": float(row['variation']),
                "Volume": int(row['volume'])
            }
            for _, row in df_hausse.iterrows()
        ]
        
        baisses = [
            {
                "Symbole": row['symbole'],
                "Prix": float(row['prix_cloture']),
                "Variation_PCT": float(row['variation']),
                "Volume": int(row['volume'])
            }
            for _, row in df_baisse.iterrows()
        ]
        
        db.kpi_trading_movers.update_one(
            {"Type": "Top_Movers"},
            {"$set": {
                "Top_Hausses": hausses,
                "Top_Baisses": baisses,
                "Derniere_MAJ": datetime.now()
            }}, upsert=True)
        
        print(f"✅ Top movers: {len(hausses)} hausses, {len(baisses)} baisses")
        
    except Exception as e:
        print(f"❌ Erreur sync_top_movers: {e}")


# ============================================================
# FONCTIONS EXISTANTES (DASHBOARD PRINCIPAL)
# ============================================================

def sync_prices():
    """Synchronise les prix et variations"""
    try:
        query = """
        SELECT symbole,
               argMax(prix_cloture, date) as dernier_prix,
               round(((argMax(prix_cloture, date) - argMax(prix_ouverture, date)) / argMax(prix_ouverture, date)) * 100, 2) as variation_journaliere,
               round(stddevPop(variation), 4) as volatilite_30j,
               round(avg(volume), 0) as volume_moyen_30j,
               round(avg(prix_cloture), 2) as prix_moyen_global
        FROM bourse.prices GROUP BY symbole
        """
        df = ch_client.query_df(query)
        
        for _, row in df.iterrows():
            db.kpi_prices.update_one(
                {"Symbole": row['symbole']},
                {"$set": {
                    "KPI_Prices": {
                        "Dernier_Prix": float(row['dernier_prix']),
                        "Variation_PCT": float(row['variation_journaliere']),
                        "Volatilite_30J": float(row['volatilite_30j']),
                        "Volume_Moyen_30J": float(row['volume_moyen_30j']),
                        "Prix_Moyen_Global": float(row['prix_moyen_global'])
                    },
                    "Derniere_MAJ": datetime.now()
                }}, upsert=True)
    except Exception as e:
        print(f"❌ Erreur sync_prices: {e}")


def sync_fundamentals():
    """Synchronise les données fondamentales"""
    try:
        query = """
        SELECT symbole, nom, secteur,
               ifNull(round((resultat_net / nullIf(revenu_total, 0)) * 100, 2), 0) as marge_net,
               ifNull(round(rentabilite_fonds_propres_roe / 100, 4), 0) as roe_norm,
               ifNull(round(total_passifs / nullIf(capitaux_propres, 0), 2), 0) as ratio_dette,
               ifNull(round(ratio_courant / 100, 2), 0) as current_ratio_norm,
               revenu_total,
               benefice_par_action,
               dividendes
        FROM bourse.fundamentals_analytics
        """
        
        df = ch_client.query_df(query).groupby('symbole').first().reset_index()
        
        for _, row in df.iterrows():
            db.kpi_fundamentals.update_one(
                {"Symbole": row['symbole']},
                {"$set": {
                    "Identity": {"Nom": row['nom'], "Secteur": row['secteur']},
                    "KPI_Fundamentals": {
                        "Marge_Beneficiaire_PCT": float(row['marge_net']),
                        "ROE_Decimal": float(row['roe_norm']),
                        "Ratio_Dette_Equity": float(row['ratio_dette']),
                        "Ratio_Courant": float(row['current_ratio_norm']),
                        "Chiffre_Affaires": float(row['revenu_total']),
                        "EPS": float(row['benefice_par_action']),
                        "Dividendes": float(row['dividendes'])
                    },
                    "Derniere_MAJ": datetime.now()
                }}, upsert=True)
    except Exception as e:
        print(f"❌ Erreur sync_fundamentals: {e}")


def sync_momentum():
    """Calcule RSI, RVOL, Performance"""
    try:
        query = """
        WITH step1 AS (
            SELECT symbole, date, prix_cloture, volume,
                   prix_cloture - lagInFrame(prix_cloture, 1) OVER (PARTITION BY symbole ORDER BY date) as diff
            FROM bourse.prices
        ),
        step2 AS (
            SELECT symbole, date, prix_cloture, volume,
                   avg(if(diff > 0, diff, 0)) OVER (PARTITION BY symbole ORDER BY date ROWS BETWEEN 14 PRECEDING AND CURRENT ROW) as avg_gain,
                   avg(if(diff < 0, abs(diff), 0)) OVER (PARTITION BY symbole ORDER BY date ROWS BETWEEN 14 PRECEDING AND CURRENT ROW) as avg_loss,
                   lagInFrame(prix_cloture, 5) OVER (PARTITION BY symbole ORDER BY date) as price_5j_ago,
                   avg(volume) OVER (PARTITION BY symbole ORDER BY date ROWS BETWEEN 30 PRECEDING AND 1 PRECEDING) as avg_vol_30j,
                   min(prix_cloture) OVER (PARTITION BY symbole ORDER BY date ROWS BETWEEN 30 PRECEDING AND CURRENT ROW) as min_30j,
                   max(prix_cloture) OVER (PARTITION BY symbole ORDER BY date ROWS BETWEEN 30 PRECEDING AND CURRENT ROW) as max_30j
            FROM step1
        )
        SELECT symbole,
               round(((prix_cloture - price_5j_ago) / nullIf(price_5j_ago, 0)) * 100, 2) as perf_5j,
               round(volume / nullIf(avg_vol_30j, 0), 2) as rvol,
               round(100 - (100 / (1 + (avg_gain / nullIf(avg_loss, 0)))), 2) as rsi,
               round(((min_30j - max_30j) / nullIf(max_30j, 0)) * 100, 2) as max_drawdown
        FROM step2 WHERE date = (SELECT max(date) FROM bourse.prices)
        """
        
        df = ch_client.query_df(query).fillna(0)
        
        for _, row in df.iterrows():
            db.kpi_momentum.update_one(
                {"Symbole": row['symbole']},
                {"$set": {
                    "KPI_Momentum": {
                        "Performance_5J_PCT": float(row['perf_5j']),
                        "Volume_Relatif_RVOL": float(row['rvol']),
                        "RSI_14J": float(row['rsi']),
                        "Max_Drawdown_30J_PCT": float(row['max_drawdown'])
                    },
                    "Derniere_MAJ": datetime.now()
                }}, upsert=True)
    except Exception as e:
        print(f"❌ Erreur sync_momentum: {e}")


def sync_investment():
    """Calcule CAGR, volatilité, score solidité"""
    try:
        # Vérifier que la table prices a des données
        count_query = "SELECT count(*) FROM bourse.prices"
        count_result = ch_client.query(count_query)
        
        if not count_result.result_rows or count_result.result_rows[0][0] == 0:
            print("⚠️ Table bourse.prices vide")
            return
        
        # Requête simplifiée et robuste pour le CAGR
        query_prices = """
        WITH price_stats AS (
            SELECT 
                symbole,
                min(date) as date_min,
                max(date) as date_max,
                argMin(prix_cloture, date) as prix_init,
                argMax(prix_cloture, date) as prix_final,
                dateDiff('day', min(date), max(date)) as nb_jours,
                stddevPop(variation) as sigma_daily
            FROM bourse.prices
            GROUP BY symbole
            HAVING prix_init > 0 AND prix_final > 0 AND nb_jours > 365
        ),
        drawdown_calc AS (
            SELECT
                symbole,
                prix_cloture,
                max(prix_cloture) OVER (PARTITION BY symbole ORDER BY date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) as max_so_far
            FROM bourse.prices
        )
        SELECT 
            ps.symbole,
            -- CAGR = ((Prix Final / Prix Initial) ^ (365 / Nb Jours)) - 1
            round((pow(ps.prix_final / ps.prix_init, 365.0 / ps.nb_jours) - 1) * 100, 2) as cagr,
            round(ps.sigma_daily * sqrt(252) * 100, 2) as vol_annualisee,
            round(min((dc.prix_cloture - dc.max_so_far) / nullIf(dc.max_so_far, 0)) * 100, 2) as max_drawdown_hist
        FROM price_stats ps
        LEFT JOIN drawdown_calc dc ON ps.symbole = dc.symbole
        GROUP BY ps.symbole, ps.prix_final, ps.prix_init, ps.nb_jours, ps.sigma_daily
        """
        
        print("📊 Calcul des métriques d'investissement...")
        df_prices = ch_client.query_df(query_prices)
        
        if df_prices.empty:
            print("⚠️ Aucune donnée de prix pour calculer CAGR")
            return
        
        print(f"   → {len(df_prices)} symboles avec historique suffisant")
        
        # Récupérer les données fondamentales pour le score
        df_fund = ch_client.query_df("""
            SELECT 
                symbole, 
                rentabilite_fonds_propres_roe as roe, 
                marge_beneficiaire, 
                total_passifs / nullIf(capitaux_propres, 0) as ratio_dette 
            FROM bourse.fundamentals_analytics
        """)
        
        df_fund = df_fund.groupby('symbole').first().reset_index()

        count = 0
        for _, row in df_prices.iterrows():
            symbole = row['symbole']
            
            # Calculer le score de solidité
            fund_row = df_fund[df_fund['symbole'] == symbole]
            score = 0
            
            if not fund_row.empty:
                f = fund_row.iloc[0]
                if pd.notnull(f['roe']) and f['roe'] > 15:
                    score += 33
                if pd.notnull(f['marge_beneficiaire']) and f['marge_beneficiaire'] > 10:
                    score += 33
                if pd.notnull(f['ratio_dette']) and f['ratio_dette'] < 0.5:
                    score += 34

            # Sauvegarder dans MongoDB
            db.kpi_investment.update_one(
                {"Symbole": symbole},
                {"$set": {
                    "KPI_Investment": {
                        "CAGR_Annualise_PCT": float(row['cagr']) if pd.notnull(row['cagr']) else 0,
                        "Volatilite_Annualisee_PCT": float(row['vol_annualisee']) if pd.notnull(row['vol_annualisee']) else 0,
                        "Max_Drawdown_Historique_PCT": float(row['max_drawdown_hist']) if pd.notnull(row['max_drawdown_hist']) else 0,
                        "Score_Solidite_Financiere": int(score)
                    },
                    "Derniere_MAJ": datetime.now()
                }}, upsert=True)
            
            count += 1
        
        print(f"✅ Investment: {count} symboles")
        
    except Exception as e:
        print(f"❌ Erreur sync_investment: {e}")
        import traceback
        traceback.print_exc()

# ============================================================
# BOUCLE PRINCIPALE
# ============================================================

if __name__ == "__main__":
    print("🚀 Démarrage de la synchronisation en temps réel")
    print("⚠️  MODE DEMO : Données historiques 2010-2016\n")
    
    # === INITIALISATION ===
    print("📊 Phase d'initialisation...")
    
    print("1/9 - Chargement OHLCV (toutes les données)...")
    sync_ohlcv_history(days=None)
    
    print("2/9 - Synchronisation des prix...")
    sync_prices()
    
    print("3/9 - Synchronisation des fondamentaux...")
    sync_fundamentals()
    
    print("4/9 - Calcul du momentum (RSI)...")
    sync_momentum()
    
    print("5/9 - Calcul des métriques investissement...")  # ← AJOUTÉ
    sync_investment()  # ← AJOUTÉ ICI
    
    print("6/9 - Calcul des indicateurs de trading...")
    sync_trading_indicators()
    
    print("7/9 - Génération des signaux...")
    sync_trading_signals()
    
    print("8/9 - Calcul de la heatmap sectorielle...")
    sync_sector_heatmap()
    
    print("9/9 - Calcul des top movers...")
    sync_top_movers()
    
    print("\n✅ Initialisation terminée!\n")
    
    cycle_count = 0
    
    while True:
        try:
            start_time = time.time()
            
            print(f"\n🔄 Cycle {cycle_count + 1}")
            
            # Synchro rapide (toutes les 5s)
            sync_prices()
            sync_momentum()
            sync_trading_indicators()
            sync_trading_signals()
            
            # Synchro approfondie (toutes les 30s)
            if cycle_count % 6 == 0:
                print("   📊 Synchro approfondie...")
                sync_fundamentals()
                sync_investment()
                sync_sector_heatmap()
                sync_top_movers()
                print("   ✅ Synchro approfondie terminée")
            
            duration = round(time.time() - start_time, 2)
            print(f"✅ Cycle terminé en {duration}s")
            
            cycle_count += 1
            time.sleep(5)
            
        except Exception as e:
            print(f"❌ Erreur: {e}")
            import traceback
            traceback.print_exc()
            time.sleep(5)