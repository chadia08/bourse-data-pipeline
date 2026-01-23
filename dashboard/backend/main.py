from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import clickhouse_connect
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

app = FastAPI(title="Bourse Analytics API - ClickHouse Only")

# Configuration CORS pour autoriser le frontend
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

# Fonction pour obtenir une connexion fraîche à ClickHouse
def get_db_client():
    try:
        client = clickhouse_connect.get_client(
            host=os.getenv("CLICKHOUSE_HOST", "localhost"),
            port=int(os.getenv("CLICKHOUSE_PORT", 8123)),
            username=os.getenv("CLICKHOUSE_USER", "default"),
            password=os.getenv("CLICKHOUSE_PASSWORD", ""),
            database=os.getenv("CLICKHOUSE_DB", "bourse")
        )
        return client
    except Exception as e:
        print(f"❌ ERREUR CRITIQUE DE CONNEXION CLICKHOUSE : {str(e)}")
        # On lève une erreur HTTP s'il n'y a pas de BDD. Pas de fausse donnée !
        raise HTTPException(
            status_code=500, 
            detail=f"Impossible de se connecter à ClickHouse. Vérifiez vos identifiants ou si le serveur tourne. Erreur: {str(e)}"
        )

@app.get("/")
def read_root():
    return {"status": "online", "source": "ClickHouse ONLY"}

@app.get("/api/companies")
def get_companies(sector: str = None, search: str = None):
    """
    Récupère la liste des sociétés directement depuis ClickHouse.
    Jointure entre la table 'company' et les dernières données de 'prices_analytics'.
    """
    client = get_db_client()
    
    # Requête SQL optimisée pour ClickHouse
    # On récupère les infos société + le dernier prix connu
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
        -- On prend la ligne la plus récente pour chaque symbole
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
        # Recherche insensible à la casse
        query += " AND (c.nom ILIKE {search:String} OR c.symbole ILIKE {search:String})"
        parameters['search'] = f"%{search}%"
    
    query += " ORDER BY c.nom ASC"

    try:
        result = client.query(query, parameters=parameters)
        
        # Transformation du résultat (liste de listes) en liste de dictionnaires JSON
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
        print(f"❌ Erreur lors de la requête SQL : {e}")
        raise HTTPException(status_code=500, detail=f"Erreur SQL ClickHouse: {str(e)}")

@app.get("/api/sectors")
def get_sectors():
    client = get_db_client()
    query = "SELECT DISTINCT secteur FROM bourse.company ORDER BY secteur"
    try:
        result = client.query(query)
        # Aplatir la liste de listes en liste simple de strings
        return [row[0] for row in result.result_rows if row[0]]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))