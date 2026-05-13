# ============================================================
#  entreprise.py — Fonctions Entreprise
#  StageLink · Gestionnaire d'emploi du temps collaboratif
# ============================================================

import re
import data
import evenements as ev_mod
from authentification import _get_all_users_of


EMAIL_PATTERN = r"^[\w\.-]+@[\w\.-]+\.\w+$"


def menu_entreprise(uid, user_info):
    """Menu principal de l'entreprise."""

    if not user_info.get("email_verified", True):
        print("\n[!] Votre adresse email n'est pas encore vérifiée.")
        print("    Veuillez vérifier votre email depuis le menu de connexion.")
        return

    if not user_info.get("verified"):
        print("\n[!] Votre compte est en attente de vérification par un administrateur.")
        print("    Vous ne pouvez pas accéder aux fonctionnalités pour l'instant.")
        return

    while True:
        _afficher_resume(uid)
        print("\n╔══════════════════════════════════════╗")
        print("║         MENU ENTREPRISE              ║")
        print("╠══════════════════════════════════════╣")
        print("║  1. Mon profil                       ║")
        print("║  2. Modifier mon profil              ║")
        print("║  — Planification —                   ║")
        print("║  3. Planifier un entretien           ║")
        print("║  4. Planifier une réunion            ║")
        print("║  5. Mes événements planifiés         ║")
        print("║  6. Modifier un événement            ║")
        print("║  7. Annuler un événement             ║")
        print("║  8. Disponibilités étudiants         ║")
        print("║  9. Rechercher un événement          ║")
        print("╠══════════════════════════════════════╣")
        print("║  0. Déconnexion                      ║")
        print("╚══════════════════════════════════════╝")

        choix = input("Votre choix : ").strip()
        mes_ids = _mes_event_ids(uid)

        if choix == "1":
            afficher_profil(uid, user_info)
        elif choix == "2":
            modifier_profil(uid, user_info)
        elif choix == "3":
            _planifier_entretien(uid)
        elif choix == "4":
            ev_mod.creer_evenement("entreprise", uid)
        elif choix == "5":
            ev_mod.afficher_tous(filtre_ids=mes_ids)
        elif choix == "6":
            ev_mod.modifier_evenement("entreprise", uid)
        elif choix == "7":
            ev_mod.supprimer_evenement("entreprise", uid)
        elif choix == "8":
            _disponibilites_etudiants()
        elif choix == "9":
            ev_mod.rechercher_evenement(filtre_ids=mes_ids)
        elif choix == "0":
            print("[✓] Déconnexion réussie.")
            break
        else:
            print("[!] Option invalide.")


def afficher_profil(uid, info):
    print("\n─── Mon profil entreprise ───")
    print(f"  ID       : {uid}")
    print(f"  Nom      : {info['nom']}")
    print(f"  Email    : {info['email']}")
    print(f"  Secteur  : {info.get('secteur', '—')}")
    statut = "✓ Vérifiée" if info.get("verified") else "⏳ En attente"
    email_status = "✓ Email vérifié" if info.get("email_verified", True) else "✗ Email non vérifié"
    print(f"  Statut   : {statut}")
    print(f"  Email    : {email_status}")


def modifier_profil(uid, info):
    print("\n─── Modifier mon profil ───")
    print("Laissez vide pour conserver.")

    nouveau_nom = input(f"Nom [{info.get('nom', '')}] : ").strip()
    if nouveau_nom:
        info["nom"] = nouveau_nom

    nouvel_email = input(f"Email [{info.get('email', '')}] : ").strip()
    if nouvel_email:
        if not _email_valide(nouvel_email):
            print("[!] Format email invalide. Email non modifié.")
        elif _email_utilise_par_autre(nouvel_email, uid):
            print("[!] Cet email est déjà utilisé. Email non modifié.")
        else:
            info["email"] = nouvel_email
            info["email_verified"] = False
            print("[!] Email modifié. Il devra être revérifié à la prochaine connexion.")

    nouveau_password = input("Mot de passe [laisser vide pour conserver] : ").strip()
    if nouveau_password:
        confirmation = input("Confirmer le nouveau mot de passe : ").strip()
        if nouveau_password == confirmation:
            info["password"] = nouveau_password
        else:
            print("[!] Les mots de passe ne correspondent pas. Mot de passe non modifié.")

    nouveau_secteur = input(f"Secteur [{info.get('secteur', '')}] : ").strip()
    if nouveau_secteur:
        info["secteur"] = nouveau_secteur

    data.save()
    print("[✓] Profil mis à jour.")


def _planifier_entretien(uid):
    """Planifie un entretien et invite des étudiants."""
    print("\n─── Planifier un entretien de stage ───")
    _afficher_etudiants()

    titre = input("Titre de l'entretien : ").strip() or "Entretien de stage"
    date = input("Date (YYYY-MM-DD) : ").strip()
    heure = input("Heure (HH:MM) : ").strip()
    lieu = input("Lieu / lien Zoom : ").strip()
    desc = input("Description du poste : ").strip()

    if not date or not heure or not lieu:
        print("[!] Date, heure et lieu sont obligatoires.")
        return

    raw = input("IDs des étudiants invités (séparés par virgule) : ").strip()
    partage = _extraire_ids_etudiants_valides(raw)

    if not partage:
        print("[!] Aucun étudiant valide sélectionné. Entretien annulé.")
        return

    conflits = _detecter_conflits(partage, date, heure)
    if conflits:
        print("\n[!] Attention : conflit détecté pour ce créneau.")
        for nom, titre_ev in conflits:
            print(f"    - {nom} a déjà : {titre_ev}")
        confirmer = input("Créer quand même l'entretien ? (o/n) : ").strip().lower()
        if confirmer != "o":
            print("[i] Création annulée.")
            return

    nid = data.next_ids["evenements"]
    data.evenements.append({
        "id": nid,
        "titre": titre,
        "type": "entretien",
        "date": date,
        "heure": heure,
        "lieu": lieu,
        "description": desc,
        "createur_role": "entreprise",
        "createur_id": uid,
        "partage_avec": partage,
        "groupe": None,
        "statut": "planifie",
    })
    data.next_ids["evenements"] += 1
    data.save()

    noms_invites = [_trouver_etudiant(eid)["nom"] for eid in partage if _trouver_etudiant(eid)]
    print(f"[✓] Entretien planifié (ID={nid}).")
    print(f"    Invités : {', '.join(noms_invites)}")


def _disponibilites_etudiants():
    """Affiche les créneaux occupés d'un étudiant sur une date."""
    _afficher_etudiants()
    try:
        eid = int(input("ID de l'étudiant : ").strip())
    except ValueError:
        print("[!] ID invalide.")
        return

    etudiant = _trouver_etudiant(eid)
    if not etudiant:
        print("[!] Étudiant introuvable.")
        return

    date = input("Date (YYYY-MM-DD) : ").strip()
    if not date:
        print("[!] Date obligatoire.")
        return

    creneaux = [
        e for e in data.evenements
        if e["date"] == date and (
            (e["createur_role"] == "etudiant" and e["createur_id"] == eid)
            or eid in e.get("partage_avec", [])
            or (etudiant.get("groupe") and e.get("groupe") == etudiant.get("groupe"))
        )
    ]

    if not creneaux:
        print(f"  {etudiant['nom']} est libre le {date} (aucun événement enregistré).")
    else:
        print(f"\n  Créneaux occupés de {etudiant['nom']} le {date} :")
        for ev in sorted(creneaux, key=lambda x: x["heure"]):
            print(f"    {ev['heure']} — {ev['titre']} ({ev['type']})")


def _afficher_resume(uid):
    mes_events = [e for e in data.evenements if e["createur_role"] == "entreprise" and e["createur_id"] == uid]
    print("\n─── Résumé entreprise ───")
    print(f"  Événements créés : {len(mes_events)}")
    if mes_events:
        prochain = sorted(mes_events, key=lambda e: (e["date"], e["heure"]))[0]
        print(f"  Prochain événement : {prochain['date']} {prochain['heure']} — {prochain['titre']}")


def _mes_event_ids(uid):
    return {
        e["id"] for e in data.evenements
        if e["createur_role"] == "entreprise" and e["createur_id"] == uid
    }


def _afficher_etudiants():
    print("  Étudiants disponibles :")
    if not data.etudiants:
        print("    (Aucun étudiant enregistré)")
        return
    for eid, einfo in _get_all_users_of(data.etudiants):
        print(f"    ID={eid} | {einfo['nom']} | {einfo.get('ecole', '—')} | {einfo.get('groupe', '—')}")


def _trouver_etudiant(eid):
    for etudiant in data.etudiants:
        if etudiant["id"] == eid:
            return etudiant
    return None


def _extraire_ids_etudiants_valides(raw):
    if not raw:
        return []

    ids_valides = []
    ids_invalides = []

    for morceau in raw.split(","):
        morceau = morceau.strip()
        if not morceau:
            continue
        try:
            eid = int(morceau)
        except ValueError:
            ids_invalides.append(morceau)
            continue

        if not _trouver_etudiant(eid):
            ids_invalides.append(str(eid))
        elif eid not in ids_valides:
            ids_valides.append(eid)

    if ids_invalides:
        print(f"[!] IDs ignorés car invalides ou introuvables : {', '.join(ids_invalides)}")

    return ids_valides


def _detecter_conflits(ids_etudiants, date, heure):
    conflits = []
    for eid in ids_etudiants:
        etudiant = _trouver_etudiant(eid)
        for ev in data.evenements:
            concerne_etudiant = (
                (ev["createur_role"] == "etudiant" and ev["createur_id"] == eid)
                or eid in ev.get("partage_avec", [])
                or (etudiant and etudiant.get("groupe") and ev.get("groupe") == etudiant.get("groupe"))
            )
            if concerne_etudiant and ev["date"] == date and ev["heure"] == heure:
                conflits.append((etudiant["nom"], ev["titre"]))
    return conflits


def _email_valide(email):
    return re.match(EMAIL_PATTERN, email) is not None


def _email_utilise_par_autre(email, current_uid):
    for role, liste in [
        ("admin", data.administrateurs),
        ("etudiant", data.etudiants),
        ("entreprise", data.entreprises),
    ]:
        for uid, info in _get_all_users_of(liste):
            if role == "entreprise" and uid == current_uid:
                continue
            if info["email"].lower() == email.lower():
                return True
    return False
