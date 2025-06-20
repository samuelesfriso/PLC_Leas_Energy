from opcua import Client
import json
from datetime import datetime
import pytz
import requests
from dotenv import load_dotenv
import os

load_dotenv() 
# Parametri di connessione
OPC_SERVER_URL = os.getenv("OPC_SERVER_URL")
API_URL = os.getenv("API_URL")
NODI_DA_LEGGERE = {
    "Pressione": 'ns=3;s="Festo"."IOLink_SFAM"[1]."Sts"."Pressure"',
    "Consumption": 'ns=3; s="Festo"."IOLink_SFAM"[1]."Sts"."Consumption"',
    "AirFlow": 'ns=3; s="Festo"."IOLink_SFAM"[1]."Sts"."AirFlow"',
}
JSON_FILE = "dati_plc_aria.json"

INTESTAZIONI = ["Timestamp"] + list(NODI_DA_LEGGERE.keys())
def invia_dati_api(dati, url):
    headers = {'Content-Type': 'application/json'}  # Aggiungi altri headers se servono (es. Authorization)
    try:
        response = requests.post(url, json=dati, headers=headers)
        response.raise_for_status()  # Lancia eccezione se status code è 4xx o 5xx
        print("Dati inviati con successo:", response.status_code)
    except requests.RequestException as e:
        print("Errore durante l'invio dei dati:", e)

def leggi_valori_da_plc(client, nodi):
    valori = {}
    for nome_logico, node_id in nodi.items():
        nodo = client.get_node(node_id)
        valore = nodo.get_value()
        if isinstance(valore, float):
            valore = round(valore, 3)
        valori[nome_logico] = valore
    return valori

def scrivi_json(dati, nome_file):
    with open(nome_file, 'w', encoding='utf-8') as f:
        json.dump(dati, f, ensure_ascii=False, indent=4)

def main():
    client = Client(OPC_SERVER_URL)
    client.set_user(os.getenv("OPC_UA_USERNAME"))
    client.set_password(os.getenv("OPC_UA_PASSWORD"))
    try:
        client.connect()
        print("Connesso al PLC.")

        # Lettura valori
        valori = leggi_valori_da_plc(client, NODI_DA_LEGGERE)
        ora_locale = datetime.now(pytz.timezone("Europe/Rome"))
        valori["Timestamp"] = ora_locale.strftime("%Y-%m-%d %H:%M:%S")

        # Ricostruisci dizionario ordinato secondo INTESTAZIONI
        dati_ordinati = {k: valori.get(k, "") for k in INTESTAZIONI}

        # Scrittura su JSON
        scrivi_json(dati_ordinati, JSON_FILE)
        invia_dati_api(dati_ordinati, API_URL)
        print("Dati salvati su JSON.")
    except Exception as e:
        print("Errore:", e)
    finally:
        client.disconnect()
        print("Disconnesso dal PLC.")

if __name__ == "__main__":
    main()