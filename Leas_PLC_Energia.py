from opcua import Client
import csv
from datetime import datetime

# Parametri di connessione
OPC_SERVER_URL = "opc.tcp://192.168.0.1:4840"  # Modifica con l'IP del tuo PLC
NODI_DA_LEGGERE = {
    "Temperatura": "ns=2;s=Sensor.Temperature",
    "Pressione": "ns=2;s=Sensor.Pressure",
    "Stato_Motore": "ns=2;s=Motor.Status"
}
CSV_FILE = "dati_plc.csv"

def leggi_valori_da_plc(client, nodi):
    valori = {}
    for nome_logico, node_id in nodi.items():
        nodo = client.get_node(node_id)
        valore = nodo.get_value()
        valori[nome_logico] = valore
    return valori

def scrivi_csv(intestazioni, dati, nome_file):
    file_esistente = False
    try:
        with open(nome_file, 'r'):
            file_esistente = True
    except FileNotFoundError:
        pass

    with open(nome_file, mode='a', newline='') as file_csv:
        writer = csv.DictWriter(file_csv, fieldnames=intestazioni)
        if not file_esistente:
            writer.writeheader()
        writer.writerow(dati)

def main():
    client = Client(OPC_SERVER_URL)
    try:
        client.connect()
        print("Connesso al PLC.")

        # Lettura valori
        valori = leggi_valori_da_plc(client, NODI_DA_LEGGERE)
        valori["Timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Scrittura su CSV
        intestazioni = list(valori.keys())
        scrivi_csv(intestazioni, valori, CSV_FILE)

        print("Dati salvati su CSV.")
    except Exception as e:
        print("Errore:", e)
    finally:
        client.disconnect()
        print("Disconnesso dal PLC.")

if __name__ == "__main__":
    main()