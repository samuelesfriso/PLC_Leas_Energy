#!/usr/bin/env python3

from opcua import Client
import csv
from datetime import datetime
import pytz

# Parametri di connessione
OPC_SERVER_URL = "opc.tcp://192.168.63.27:4840"  # Modifica con l'IP del tuo PLC
NODI_DA_LEGGERE = {
    "rP_1": 'ns=3; s="EnergyMeter"."EnergyMeter"[1]."STS"."ReactivePowerL1"',
    "rP_2": 'ns=3; s="EnergyMeter"."EnergyMeter"[1]."STS"."ReactivePowerL2"',
    "rP_3": 'ns=3; s="EnergyMeter"."EnergyMeter"[1]."STS"."ReactivePowerL3"',
    "apP_1": 'ns=3; s="EnergyMeter"."EnergyMeter"[1]."STS"."ApparentPowerL1"',
    "apP_2": 'ns=3; s="EnergyMeter"."EnergyMeter"[1]."STS"."ApparentPowerL2"',
    "apP_3": 'ns=3; s="EnergyMeter"."EnergyMeter"[1]."STS"."ApparentPowerL3"',
    "aP_1": 'ns=3; s="EnergyMeter"."EnergyMeter"[1]."STS"."ActivePowerL1"',
    "aP_2": 'ns=3; s="EnergyMeter"."EnergyMeter"[1]."STS"."ActivePowerL2"',
    "aP_3": 'ns=3; s="EnergyMeter"."EnergyMeter"[1]."STS"."ActivePowerL3"',
    "v_1": 'ns=3; s="EnergyMeter"."EnergyMeter"[1]."STS"."VoltageN-L1"',
    "v_2": 'ns=3; s="EnergyMeter"."EnergyMeter"[1]."STS"."VoltageN-L2"',
    "v_3": 'ns=3; s="EnergyMeter"."EnergyMeter"[1]."STS"."VoltageN-L3"',
    "v_12": 'ns=3; s="EnergyMeter"."EnergyMeter"[1]."STS"."VoltageL1-L2"',
    "v_13": 'ns=3; s="EnergyMeter"."EnergyMeter"[1]."STS"."VoltageL3-L1"',
    "v_23": 'ns=3; s="EnergyMeter"."EnergyMeter"[1]."STS"."VoltageL2-L3"',
    "c_1": 'ns=3; s="EnergyMeter"."EnergyMeter"[1]."STS"."CurrentL1"',
    "c_2": 'ns=3; s="EnergyMeter"."EnergyMeter"[1]."STS"."CurrentL2"',
    "c_3": 'ns=3; s="EnergyMeter"."EnergyMeter"[1]."STS"."CurrentL3"',
    "Tot_Energy": 'ns=3; s="EnergyMeter"."EnergyMeter"[1]."STS"."TotalActiveEnergyL1L2L3"'
}
CSV_FILE = "dati_plc_automation.csv"

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