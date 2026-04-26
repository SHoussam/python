# ============================================================
#  storage.py — Lecture & sauvegarde du fichier JSON
#  StageLink · Gestionnaire d'emploi du temps collaboratif
# ============================================================

import json
from pathlib import Path

# Chemin du fichier data.json placé dans le même dossier que ce fichier.
BASE_DIR = Path(__file__).resolve().parent
FILE = BASE_DIR / "data.json"


def load_data():
    """Charge les données depuis data.json et les retourne sous forme de dictionnaire."""
    try:
        with open(FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("[!] Fichier data.json introuvable. Données vides chargées.")
        return {}
    except json.JSONDecodeError:
        print("[!] data.json est invalide ou vide. Données vides chargées.")
        return {}


def save_data(data):
    """Sauvegarde le dictionnaire Python reçu dans data.json."""
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
