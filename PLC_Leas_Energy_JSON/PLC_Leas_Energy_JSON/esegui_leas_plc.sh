#!/bin/bash

# Timestamp iniziale
echo "Script avviato alle $(date)" >> /tmp/debug_leas.log

# Attivazione del virtual environment
#source /home/vboxuser/Documents/Lavoro/venv/bin/activate
#source /app

# Percorso alla directory degli script
#SCRIPT_DIR="/home/vboxuser/Documents/Lavoro/venv/PLC_Leas_Energy_JSON"
#LOG_FILE="/tmp/debug_leas.log"
# Esecuzione degli script Python con log
python "PLC_saldatura_prova_json.py"  #>>"$LOG_FILE" 2>&1
python "PLC_automation_prova_json.py" #>> "$LOG_FILE" 2>&1
python "PLC_Aria_prova_json.py" #>> "$LOG_FILE" 2>&1



