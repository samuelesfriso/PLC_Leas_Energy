#!/usr/bin/env python3

from opcua import Client
import csv
from datetime import datetime
import pytz

# Parametri di connessione
OPC_SERVER_URL = "opc.tcp://192.168.63.27:4840"  # Modifica con l'IP del tuo PLC
NODI_DA_LEGGERE = {
    "Pressione": 'ns=3;s="Festo"."IOLink_SFAM"[1]."Sts"."Pressure"',
    "Consumption": 'ns=3; s="Festo"."IOLink_SFAM"[1]."Sts"."Consumption"',
    "AirFlow": 'ns=3; s="Festo"."IOLink_SFAM"[1]."Sts"."AirFlow"',
}
CSV_FILE = "dati_plc_aria.csv"

INTESTAZIONI = ["Timestamp"] + list(NODI_DA_LEGGERE.keys())

def leggi_valori_da_plc(client, nodi):
    valori = {}
    for nome_logico, node_id in nodi.items():
        nodo = client.get_node(node_id)
        valore = nodo.get_value()
        if isinstance(valore, float):
            valore = f"{valore:.3f}".replace('.', ',')
        else:
            valore = str(valore)

        valori[nome_logico] = valore
    return valori

def scrivi_csv(intestazioni, dati, nome_file):
    file_esistente = False
    try:
        with open(nome_file, 'r', encoding='utf-8-sig'):
            file_esistente = True
    except FileNotFoundError:
        pass

    with open(nome_file, mode='a', newline='', encoding='utf-8-sig') as file_csv:
        writer = csv.DictWriter(file_csv, fieldnames=intestazioni, delimiter=';')
        if not file_esistente:
            writer.writeheader()
        writer.writerow(dati)

def main():
    client = Client(OPC_SERVER_URL)
    client.set_user("OPC_UA")
    client.set_password("L3asOpc_uA")
    try:
        client.connect()
        print("Connesso al PLC.")

        # Lettura valori
        valori = leggi_valori_da_plc(client, NODI_DA_LEGGERE)
        ora_locale = datetime.now(pytz.timezone("Europe/Rome"))
        valori["Timestamp"] = ora_locale.strftime("%Y-%m-%d %H:%M:%S")

        # Ricostruisci dizionario ordinato secondo INTESTAZIONI
        dati_ordinati = {k: valori.get(k, "") for k in INTESTAZIONI}

        # Scrittura su CSV
        scrivi_csv(INTESTAZIONI, dati_ordinati, CSV_FILE)

        print("Dati salvati su CSV.")
    except Exception as e:
        print("Errore:", e)
    finally:
        client.disconnect()
        print("Disconnesso dal PLC.")

if __name__ == "__main__":
    main()