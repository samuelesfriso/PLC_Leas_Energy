#!/bin/bash

# Timestamp iniziale
echo "Script avviato alle $(date)" >> /tmp/debug_leas.log

# Attivazione del virtual environment
source /home/vboxuser/Documents/Lavoro/venv/bin/activate

# Percorso alla directory degli script
SCRIPT_DIR="/home/vboxuser/Documents/Lavoro/venv/LEAS_PLC"
LOG_FILE="/tmp/debug_leas.log"

# Esecuzione degli script Python con log
python "$SCRIPT_DIR/Leas_PLC_Energia_Saldatura.py" >> "$LOG_FILE" 2>&1
python "$SCRIPT_DIR/Leas_PLC_Energia_Automation.py" >> "$LOG_FILE" 2>&1
python "$SCRIPT_DIR/Leas_PLC_Energia_Aria.py" >> "$LOG_FILE" 2>&1



