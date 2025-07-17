from opcua import Client
import json
from datetime import datetime
import pytz
import base64
import requests
from dotenv import load_dotenv
import os

load_dotenv() 
# Parametri di connessione
OPC_SERVER_URL = os.getenv("OPC_SERVER_URL")
API_URL = os.getenv("API_URL")
API_URL_POST = os.getenv ("API_URL_POST")
NODI_DA_LEGGERE = {
    "Pressione": 'ns=3;s="Festo"."IOLink_SFAM"[1]."Sts"."Pressure"',
    "Consumption": 'ns=3; s="Festo"."IOLink_SFAM"[1]."Sts"."Consumption"',
    "AirFlow": 'ns=3; s="Festo"."IOLink_SFAM"[1]."Sts"."AirFlow"',
}
JSON_FILE = "dati_plc_aria.json"

INTESTAZIONI = ["meter"]+["tsISO8601"] + list(NODI_DA_LEGGERE.keys())
def invia_dati_api(dati, url):
    username = os.getenv("API_USER")
    password = os.getenv("API_PASSWORD")

    # Codifica le credenziali in Base64 per HTTP Basic Auth
    credentials = f"{username}:{password}"
    credentials_b64 = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Basic {credentials_b64}'
    }

    try:
        response = requests.post(url, json=dati, headers=headers)
        response.raise_for_status()
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
        valori["meter"]="X3EnergyMeter"
        ora_locale = datetime.now(pytz.timezone("Europe/Rome"))
        valori["tsISO8601"] = ora_locale.strftime("%Y-%m-%d %H:%M:%S")

        # Ricostruisci dizionario ordinato secondo INTESTAZIONI
        dati_ordinati = {k: valori.get(k, "") for k in INTESTAZIONI}

        # Scrittura su JSON
        scrivi_json(dati_ordinati, JSON_FILE)
        invia_dati_api(dati_ordinati, API_URL_POST)
        print("Dati salvati su JSON.")
    except Exception as e:
        print("Errore:", e)
    finally:
        client.disconnect()
        print("Disconnesso dal PLC.")

if __name__ == "__main__":
    main()