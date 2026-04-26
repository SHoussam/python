# ============================================================
#  data.py — Stockage centralisé des données JSON
#  StageLink · Gestionnaire d'emploi du temps collaboratif
# ============================================================

import storage

# Chargement des données depuis data.json au démarrage du programme.
_data = storage.load_data()

administrateurs = _data.get("administrateurs", [])
etudiants = _data.get("etudiants", [])
entreprises = _data.get("entreprises", [])
evenements = _data.get("evenements", [])
groupes = _data.get("groupes", [])

next_ids = _data.get("next_ids", {
    "administrateurs": 1,
    "etudiants": 1,
    "entreprises": 1,
    "evenements": 1,
    "groupes": 1,
})


def save():
    """Sauvegarde l'état actuel des données dans data.json."""
    storage.save_data({
        "administrateurs": administrateurs,
        "etudiants": etudiants,
        "entreprises": entreprises,
        "evenements": evenements,
        "groupes": groupes,
        "next_ids": next_ids,
    })
