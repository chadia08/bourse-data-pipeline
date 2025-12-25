import pandas as pd

# Chargement et réduction du fichier
df = pd.read_csv('prices.csv')
df_small = df.head(200)

# Sauvegarde
df_small.to_csv('prices_reduced.csv', index=False)