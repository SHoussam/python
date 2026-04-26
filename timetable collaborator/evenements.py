# ============================================================
#  evenements.py — CRUD partagé pour les événements
#  StageLink · Gestionnaire d'emploi du temps collaboratif
# ============================================================

from datetime import datetime
import data

TYPES_VALIDES = ["entretien", "reunion", "deadline", "validation", "cours"]


# ──────────────────────────────────────────────
#  Affichage
# ──────────────────────────────────────────────

def _afficher_evenement(ev):
    print(f"\n  ┌─ ID {ev['id']} ─────────────────────────────")
    print(f"  │  📌 {ev['titre']}")
    print(f"  │  Type     : {ev['type']}")
    print(f"  │  Date     : {ev['date']} à {ev['heure']}")
    print(f"  │  Lieu     : {ev['lieu']}")
    print(f"  │  Desc.    : {ev['description']}")
    print(f"  │  Créé par : {ev['createur_role']} #{ev['createur_id']}")
    if ev.get("partage_avec"):
        print(f"  │  Invités  : {', '.join(map(str, ev['partage_avec']))}")
    if ev.get("groupe"):
        print(f"  │  Groupe   : {ev['groupe']}")
    print("  └────────────────────────────────────────")


def afficher_tous(filtre_ids=None):
    """Affiche tous les événements, ou ceux dont l'id est dans filtre_ids."""
    liste = [
        e for e in data.evenements
        if filtre_ids is None or e["id"] in filtre_ids
    ]
    if not liste:
        print("  (Aucun événement trouvé)")
        return

    for ev in sorted(liste, key=lambda x: (x["date"], x["heure"])):
        _afficher_evenement(ev)


def afficher_par_type(type_ev, filtre_ids=None):
    """Affiche les événements d'un type donné."""
    type_ev = type_ev.strip().lower()
    if type_ev not in TYPES_VALIDES:
        print("[!] Type invalide.")
        return

    liste = [
        e for e in data.evenements
        if e["type"] == type_ev and (filtre_ids is None or e["id"] in filtre_ids)
    ]
    if not liste:
        print(f"  (Aucun événement de type '{type_ev}')")
        return

    for ev in sorted(liste, key=lambda x: (x["date"], x["heure"])):
        _afficher_evenement(ev)


# ──────────────────────────────────────────────
#  Création
# ──────────────────────────────────────────────

def creer_evenement(role, uid):
    """Crée un nouvel événement."""
    print("\n─── Nouvel événement ───")

    titre = _saisir_obligatoire("Titre")
    if not titre:
        return

    type_ev = _saisir_type()
    if not type_ev:
        return

    date = _saisir_date()
    if not date:
        return

    heure = _saisir_heure()
    if not heure:
        return

    lieu = _saisir_obligatoire("Lieu / lien")
    if not lieu:
        return

    desc = input("Description : ").strip() or "—"

    partage = []
    if role in ("admin", "entreprise"):
        partage = _saisir_ids_etudiants()

    groupe = None
    if role == "admin":
        groupe = input("Nom du groupe concerné (ou vide) : ").strip() or None
        if groupe and not _groupe_existe(groupe):
            print("[!] Groupe introuvable. Événement non créé.")
            return

    conflits = _detecter_conflits(date, heure, partage, groupe)
    if conflits and not _confirmer_conflits(conflits):
        print("[!] Création annulée.")
        return

    nid = data.next_ids["evenements"]
    ev = {
        "id": nid,
        "titre": titre,
        "type": type_ev,
        "date": date,
        "heure": heure,
        "lieu": lieu,
        "description": desc,
        "createur_role": role,
        "createur_id": uid,
        "partage_avec": partage,
        "groupe": groupe,
    }

    data.evenements.append(ev)
    data.next_ids["evenements"] += 1
    data.save()
    print(f"[✓] Événement créé avec succès (ID={nid}).")


# ──────────────────────────────────────────────
#  Modification
# ──────────────────────────────────────────────

def modifier_evenement(role, uid):
    """Modifie un événement appartenant à l'utilisateur, ou n'importe lequel pour l'admin."""
    eid = _saisir_id("Modifier")
    ev = _trouver_evenement(eid)
    if not ev:
        return

    if not _peut_modifier(role, uid, ev):
        print("[!] Vous ne pouvez modifier que vos propres événements.")
        return

    print("Laissez vide pour conserver la valeur actuelle.")

    nouveau = ev.copy()
    nouveau_partage = list(ev.get("partage_avec", []))

    titre = input(f"Titre [{ev['titre']}] : ").strip()
    if titre:
        nouveau["titre"] = titre

    type_ev = input(f"Type [{ev['type']}] ({', '.join(TYPES_VALIDES)}) : ").strip().lower()
    if type_ev:
        if type_ev not in TYPES_VALIDES:
            print("[!] Type invalide. Modification annulée.")
            return
        nouveau["type"] = type_ev

    date = input(f"Date [{ev['date']}] (YYYY-MM-DD) : ").strip()
    if date:
        if not _date_valide(date):
            print("[!] Date invalide. Modification annulée.")
            return
        nouveau["date"] = date

    heure = input(f"Heure [{ev['heure']}] (HH:MM) : ").strip()
    if heure:
        if not _heure_valide(heure):
            print("[!] Heure invalide. Modification annulée.")
            return
        nouveau["heure"] = heure

    lieu = input(f"Lieu [{ev['lieu']}] : ").strip()
    if lieu:
        nouveau["lieu"] = lieu

    desc = input(f"Description [{ev['description']}] : ").strip()
    if desc:
        nouveau["description"] = desc

    if role in ("admin", "entreprise"):
        raw = input("Nouveaux IDs étudiants invités (vide = conserver) : ").strip()
        if raw:
            nouveau_partage = _extraire_ids_etudiants_valides(raw)
            nouveau["partage_avec"] = nouveau_partage

    if role == "admin":
        groupe = input(f"Groupe [{ev.get('groupe') or 'aucun'}] : ").strip()
        if groupe:
            if not _groupe_existe(groupe):
                print("[!] Groupe introuvable. Modification annulée.")
                return
            nouveau["groupe"] = groupe

    conflits = _detecter_conflits(
        nouveau["date"],
        nouveau["heure"],
        nouveau.get("partage_avec", []),
        nouveau.get("groupe"),
        ignore_event_id=ev["id"],
    )
    if conflits and not _confirmer_conflits(conflits):
        print("[!] Modification annulée.")
        return

    ev.update(nouveau)
    data.save()
    print("[✓] Événement modifié.")


# ──────────────────────────────────────────────
#  Suppression
# ──────────────────────────────────────────────

def supprimer_evenement(role, uid):
    """Supprime un événement si l'utilisateur est propriétaire, ou admin."""
    eid = _saisir_id("Supprimer")
    ev = _trouver_evenement(eid)
    if not ev:
        return

    if not _peut_modifier(role, uid, ev):
        print("[!] Vous ne pouvez supprimer que vos propres événements.")
        return

    confirmation = input(f"Confirmer la suppression de '{ev['titre']}' ? (o/n) : ").strip().lower()
    if confirmation != "o":
        print("[!] Suppression annulée.")
        return

    data.evenements.remove(ev)
    data.save()
    print(f"[✓] Événement ID={eid} supprimé.")


# ──────────────────────────────────────────────
#  Recherche
# ──────────────────────────────────────────────

def rechercher_evenement(filtre_ids=None):
    """Recherche par mot-clé dans le titre, la description, le lieu ou le type."""
    mot = input("Mot-clé : ").strip().lower()
    if not mot:
        print("[!] Mot-clé vide.")
        return

    resultats = [
        e for e in data.evenements
        if (
            mot in e["titre"].lower()
            or mot in e["description"].lower()
            or mot in e["lieu"].lower()
            or mot in e["type"].lower()
        ) and (filtre_ids is None or e["id"] in filtre_ids)
    ]

    if not resultats:
        print("  (Aucun résultat)")
        return

    for ev in sorted(resultats, key=lambda x: (x["date"], x["heure"])):
        _afficher_evenement(ev)


# ──────────────────────────────────────────────
#  Disponibilités
# ──────────────────────────────────────────────

def voir_disponibilites():
    """Affiche les créneaux occupés pour une date donnée."""
    date = input("Date à consulter (YYYY-MM-DD) : ").strip()
    if not _date_valide(date):
        print("[!] Date invalide.")
        return

    creneaux = [e for e in data.evenements if e["date"] == date]
    if not creneaux:
        print(f"  Aucun événement enregistré le {date}.")
        return

    print(f"\n  Créneaux occupés le {date} :")
    for ev in sorted(creneaux, key=lambda x: x["heure"]):
        cible = ""
        if ev.get("groupe"):
            cible = f" | groupe {ev['groupe']}"
        elif ev.get("partage_avec"):
            cible = f" | étudiants {ev['partage_avec']}"
        print(f"    {ev['heure']} — {ev['titre']} ({ev['type']}){cible}")


# ──────────────────────────────────────────────
#  Helpers internes
# ──────────────────────────────────────────────

def _saisir_id(action):
    try:
        return int(input(f"ID de l'événement à {action.lower()} : ").strip())
    except ValueError:
        print("[!] ID invalide.")
        return None


def _trouver_evenement(eid):
    if eid is None:
        return None
    for ev in data.evenements:
        if ev["id"] == eid:
            return ev
    print(f"[!] Événement ID={eid} introuvable.")
    return None


def _peut_modifier(role, uid, ev):
    return role == "admin" or (ev["createur_role"] == role and ev["createur_id"] == uid)


def _saisir_obligatoire(label):
    valeur = input(f"{label} : ").strip()
    if not valeur:
        print(f"[!] {label} obligatoire.")
        return None
    return valeur


def _saisir_type():
    print(f"Type ({', '.join(TYPES_VALIDES)}) : ", end="")
    type_ev = input().strip().lower()
    if type_ev not in TYPES_VALIDES:
        print("[!] Type invalide.")
        return None
    return type_ev


def _saisir_date():
    date = input("Date (YYYY-MM-DD) : ").strip()
    if not _date_valide(date):
        print("[!] Date invalide. Format attendu : YYYY-MM-DD.")
        return None
    return date


def _saisir_heure():
    heure = input("Heure (HH:MM) : ").strip()
    if not _heure_valide(heure):
        print("[!] Heure invalide. Format attendu : HH:MM.")
        return None
    return heure


def _date_valide(date):
    try:
        datetime.strptime(date, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def _heure_valide(heure):
    try:
        datetime.strptime(heure, "%H:%M")
        return True
    except ValueError:
        return False


def _saisir_ids_etudiants():
    raw = input("IDs étudiants à inviter (séparés par virgule, ou vide) : ").strip()
    if not raw:
        return []
    return _extraire_ids_etudiants_valides(raw)


def _extraire_ids_etudiants_valides(raw):
    ids_valides = []
    ids_invalides = []

    for item in raw.split(","):
        item = item.strip()
        if not item:
            continue
        try:
            eid = int(item)
        except ValueError:
            ids_invalides.append(item)
            continue

        if not _trouver_etudiant(eid):
            ids_invalides.append(str(eid))
            continue

        if eid not in ids_valides:
            ids_valides.append(eid)

    if ids_invalides:
        print(f"[!] IDs ignorés car invalides/introuvables : {', '.join(ids_invalides)}")

    return ids_valides


def _trouver_etudiant(eid):
    for etu in data.etudiants:
        if etu.get("id") == eid:
            return etu
    return None


def _groupe_existe(nom):
    return any(g.get("nom") == nom for g in data.groupes)


def _membres_groupe(nom):
    groupe = next((g for g in data.groupes if g.get("nom") == nom), None)
    return groupe.get("membres", []) if groupe else []


def _detecter_conflits(date, heure, partage, groupe, ignore_event_id=None):
    """
    Détecte les événements existants au même créneau.
    Pour l'instant, un conflit = même date + même heure.
    """
    personnes_concernees = set(partage)
    if groupe:
        personnes_concernees.update(_membres_groupe(groupe))

    conflits = []
    for ev in data.evenements:
        if ignore_event_id is not None and ev["id"] == ignore_event_id:
            continue
        if ev["date"] != date or ev["heure"] != heure:
            continue

        conflit_direct = personnes_concernees.intersection(ev.get("partage_avec", []))
        conflit_groupe = groupe and ev.get("groupe") == groupe
        conflit_avec_groupe_existant = False

        if ev.get("groupe"):
            membres = set(_membres_groupe(ev["groupe"]))
            conflit_avec_groupe_existant = bool(personnes_concernees.intersection(membres))

        if conflit_direct or conflit_groupe or conflit_avec_groupe_existant:
            conflits.append(ev)

    return conflits


def _confirmer_conflits(conflits):
    print("\n[!] Conflit(s) détecté(s) sur ce créneau :")
    for ev in conflits:
        print(f"    ID={ev['id']} | {ev['heure']} | {ev['titre']} ({ev['type']})")
    choix = input("Continuer quand même ? (o/n) : ").strip().lower()
    return choix == "o"
