#!/bin/bash

echo "Tworzenie wirtualnego środowiska..."
python3 -m venv env

echo "Aktywowanie wirtualnego środowiska..."
source env/bin/activate

echo "Instalacja bibliotek..."
pip install --upgrade pip
pip install requests

echo "Uruchamianie skryptu historia_pojazdu.py..."
python historia_pojazdu.py

