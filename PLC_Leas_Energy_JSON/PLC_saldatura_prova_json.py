#!/usr/bin/env python3

from opcua import Client
import json
from datetime import datetime
import pytz
import requests
import base64
from dotenv import load_dotenv
import os

load_dotenv() 
# Parametri di connessione
OPC_SERVER_URL = os.getenv("OPC_SERVER_URL")
API_URL = os.getenv("API_URL")
API_URL_POST = os.getenv("API_URL_POST")
NODI_DA_LEGGERE = {
    "rP_1": 'ns=3; s="EnergyMeter"."EnergyMeter"[2]."STS"."ReactivePowerL1"',
    "rP_2": 'ns=3; s="EnergyMeter"."EnergyMeter"[2]."STS"."ReactivePowerL2"',
    "rP_3": 'ns=3; s="EnergyMeter"."EnergyMeter"[2]."STS"."ReactivePowerL3"',
    "apP_1": 'ns=3; s="EnergyMeter"."EnergyMeter"[2]."STS"."ApparentPowerL1"',
    "apP_2": 'ns=3; s="EnergyMeter"."EnergyMeter"[2]."STS"."ApparentPowerL2"',
    "apP_3": 'ns=3; s="EnergyMeter"."EnergyMeter"[2]."STS"."ApparentPowerL3"',
    "aP_1": 'ns=3; s="EnergyMeter"."EnergyMeter"[2]."STS"."ActivePowerL1"',
    "aP_2": 'ns=3; s="EnergyMeter"."EnergyMeter"[2]."STS"."ActivePowerL2"',
    "aP_3": 'ns=3; s="EnergyMeter"."EnergyMeter"[2]."STS"."ActivePowerL3"',
    "v_1": 'ns=3; s="EnergyMeter"."EnergyMeter"[2]."STS"."VoltageN-L1"',
    "v_2": 'ns=3; s="EnergyMeter"."EnergyMeter"[2]."STS"."VoltageN-L2"',
    "v_3": 'ns=3; s="EnergyMeter"."EnergyMeter"[2]."STS"."VoltageN-L3"',
    "v_12": 'ns=3; s="EnergyMeter"."EnergyMeter"[2]."STS"."VoltageL1-L2"',
    "v_13": 'ns=3; s="EnergyMeter"."EnergyMeter"[2]."STS"."VoltageL3-L1"',
    "v_23": 'ns=3; s="EnergyMeter"."EnergyMeter"[2]."STS"."VoltageL2-L3"',
    "c_1": 'ns=3; s="EnergyMeter"."EnergyMeter"[2]."STS"."CurrentL1"',
    "c_2": 'ns=3; s="EnergyMeter"."EnergyMeter"[2]."STS"."CurrentL2"',
    "c_3": 'ns=3; s="EnergyMeter"."EnergyMeter"[2]."STS"."CurrentL3"',
    "Tot_Energy": 'ns=3; s="EnergyMeter"."EnergyMeter"[2]."STS"."TotalActiveEnergyL1L2L3"'
}
JSON_FILE = "dati_plc_saldatura.json"

def invia_dati_api(dati, url):
    username = os.getenv("API_USER")
    password = os.getenv("API_PASSWORD")
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
def costruisci_json_formattato(valori_raw, timestamp,nome_meter="X3EnergyMeter"):
    dati_formattati = {
        "meter": nome_meter,
        "tsISO8601": timestamp,
        "aP_1": valori_raw.get("aP_1", 0),
        "aP_2": valori_raw.get("aP_2", 0),
        "aP_3": valori_raw.get("aP_3", 0),
        "rP_1": valori_raw.get("rP_1", 0),
        "rP_2": valori_raw.get("rP_2", 0),
        "rP_3": valori_raw.get("rP_3", 0),
        "apP_1": valori_raw.get("apP_1", 0),
        "apP_2": valori_raw.get("apP_2", 0),
        "apP_ 3": valori_raw.get("apP_3", 0), 
        "v_1": valori_raw.get("v_1", 0),
        "v_2": valori_raw.get("v_2", 0),
        "v_3": valori_raw.get("v_3", 0),
        "c_1": valori_raw.get("c_1", 0),
        "c_2": valori_raw.get("c_2", 0),
        "c_3": valori_raw.get("c_3", 0),
        "pC_1": valori_raw.get("Tot_Energy",0),
        "pC_2": 0,
        "pC_3": 0,
        "v_12": valori_raw.get("v_12", 0),
        "v_13": valori_raw.get("v_13", 0),
        "v_23": valori_raw.get("v_23", 0),
        "ePreA_1": 0,
        "ePreR_1": 0,
        "eImmA_1": 0,
        "ePreRTot_1": 0,
        "eImmATot_1": 0
    }
    return dati_formattati

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
        timestamp = ora_locale.strftime("%Y-%m-%d %H:%M:%S")
        # Ricostruisci dizionario ordinato secondo INTESTAZIONI
        #dati_ordinati = {k: valori.get(k, "") for k in INTESTAZIONI}
        dati_formattati= costruisci_json_formattato(valori,timestamp, nome_meter="X3EnergyMeter")  
        # Scrittura su JSON
        scrivi_json(dati_formattati, JSON_FILE)
        invia_dati_api(dati_formattati, API_URL_POST)
        print("Dati salvati su JSON.")
    except Exception as e:
        print("Errore:", e)
    finally:
        client.disconnect()
        print("Disconnesso dal PLC.")

if __name__ == "__main__":
    main()