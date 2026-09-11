import os
import requests
import urllib.parse
import pandas as pd
import time
import matplotlib.pyplot as plt
import seaborn as sns
from dotenv import load_dotenv
from sqlalchemy import create_engine

# Cargar API
load_dotenv()
api_key = os.getenv("RIOT_API_KEY")
riot_id_name = "The Kitty King"
riot_id_tagline = "MMJ"
headers = {"X-Riot-Token": api_key}
safe_name = urllib.parse.quote(riot_id_name)

# 2. SQL Server

nombre_servidor = r"GABRIELA\SQLEXPRESS" 
nombre_bd = "PortafolioData"

# Cambiar driver a modelo 17 para más estabilidad
conexion_str = urllib.parse.quote_plus(
    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
    f"SERVER={nombre_servidor};"
    f"DATABASE={nombre_bd};"
    f"Trusted_Connection=yes;"
)
motor_sql = create_engine(
    f"mssql+pyodbc:///?odbc_connect={conexion_str}",
    isolation_level="AUTOCOMMIT"
)

# Extracción de los datos

url_puuid = f"https://americas.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{safe_name}/{riot_id_tagline}"
response_puuid = requests.get(url_puuid, headers=headers)

if response_puuid.status_code == 200:
    puuid = response_puuid.json()['puuid']
else:
    print(f"Riot nos detuvo D: Código de error: {response_puuid.status_code}")
    exit()

url_matches = f"https://americas.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count=50"
match_ids = requests.get(url_matches, headers=headers).json()

print(f"Descargando {len(match_ids)} partidas y enviando a la base de datos...\n")
mis_datos = []

for partida in match_ids:
    url_detalle = f"https://americas.api.riotgames.com/lol/match/v5/matches/{partida}"
    response = requests.get(url_detalle, headers=headers)
    
    if response.status_code == 200:
        datos = response.json()
        for jugador in datos['info']['participants']:
            if jugador['puuid'] == puuid:
                # Nombres de columnas mapeados exactamente a tu tabla SQL
                estadisticas = {
                    "Campeon": jugador['championName'],
                    "Resultado": "Victoria" if jugador['win'] else "Derrota",
                    "Kills": jugador['kills'],
                    "Deaths": jugador['deaths'],
                    "Assists": jugador['assists'],
                    "Danio_Total": jugador['totalDamageDealtToChampions'],
                    "Oro_Ganado": jugador['goldEarned']
                }
                mis_datos.append(estadisticas)
                
    time.sleep(0.8) # Pausa de seguridad

#Cargar a SQL y graficar
df = pd.DataFrame(mis_datos)

# ¡Magia! Enviamos los datos directo a la tabla
print("Insertando partidas en SQL Server...")
df.to_sql("MisPartidasLoL", con=motor_sql, if_exists="append", index=False)
print("¡Base de datos actualizada exitosamente! uwu\n")

# Dashboard visual
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

victorias_conteo = df['Resultado'].value_counts()
colores_pastel = ['#66c2a5', '#fc8d62'] if victorias_conteo.index[0] == 'Victoria' else ['#fc8d62', '#66c2a5']

axes[0].pie(victorias_conteo, labels=victorias_conteo.index, autopct='%1.1f%%', 
            colors=colores_pastel, startangle=90, textprops={'fontsize': 12, 'weight': 'bold'})
axes[0].set_title('Mi Winrate General', fontsize=14, fontweight='bold')

sns.scatterplot(data=df, x='Kills', y='Danio_Total', hue='Resultado', 
                palette={'Victoria': '#66c2a5', 'Derrota': '#fc8d62'}, 
                s=120, ax=axes[1], edgecolor='black', alpha=0.8)

axes[1].set_title('Impacto: Kills vs Daño Causado', fontsize=14, fontweight='bold')
axes[1].set_xlabel('Cantidad de Kills', fontsize=12)
axes[1].set_ylabel('Daño Total a Campeones', fontsize=12)

plt.tight_layout()
plt.show()