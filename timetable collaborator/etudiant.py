# ============================================================
#  etudiant.py — Fonctions Étudiant
#  StageLink · Gestionnaire d'emploi du temps collaboratif
# ============================================================

import re
from datetime import date

import data
import evenements as ev_mod


EMAIL_REGEX = r"^[\w\.-]+@[\w\.-]+\.\w+$"


def menu_etudiant(uid, user_info):
    """Menu principal de l'étudiant."""
    while True:
        _afficher_resume_etudiant(uid, user_info)

        print("\n╔══════════════════════════════════════╗")
        print("║         MENU ÉTUDIANT                ║")
        print("╠══════════════════════════════════════╣")
        print("║  1. Mon profil                       ║")
        print("║  2. Modifier mon profil              ║")
        print("║  3. Mon emploi du temps (tous)       ║")
        print("║  4. Mes entretiens de stage          ║")
        print("║  5. Mes deadlines importantes        ║")
        print("║  6. Réunions & validations           ║")
        print("║  7. Créer un événement personnel     ║")
        print("║  8. Modifier mon événement           ║")
        print("║  9. Supprimer mon événement          ║")
        print("║ 10. Rechercher un événement          ║")
        print("║ 11. Disponibilités (par date)        ║")
        print("║ 12. Mon groupe collaboratif          ║")
        print("╠══════════════════════════════════════╣")
        print("║  0. Déconnexion                      ║")
        print("╚══════════════════════════════════════╝")

        choix = input("Votre choix : ").strip()

        # IDs des événements accessibles à cet étudiant
        mes_ids = _mes_event_ids(uid, user_info)

        if choix == "1":
            afficher_profil(uid, user_info)
        elif choix == "2":
            modifier_profil(uid, user_info)
        elif choix == "3":
            ev_mod.afficher_tous(filtre_ids=mes_ids)
        elif choix == "4":
            ev_mod.afficher_par_type("entretien", filtre_ids=mes_ids)
        elif choix == "5":
            ev_mod.afficher_par_type("deadline", filtre_ids=mes_ids)
        elif choix == "6":
            print("\n─ Réunions ─")
            ev_mod.afficher_par_type("reunion", filtre_ids=mes_ids)
            print("\n─ Validations ─")
            ev_mod.afficher_par_type("validation", filtre_ids=mes_ids)
        elif choix == "7":
            ev_mod.creer_evenement("etudiant", uid)
        elif choix == "8":
            ev_mod.modifier_evenement("etudiant", uid)
        elif choix == "9":
            ev_mod.supprimer_evenement("etudiant", uid)
        elif choix == "10":
            ev_mod.rechercher_evenement(filtre_ids=mes_ids)
        elif choix == "11":
            ev_mod.voir_disponibilites()
        elif choix == "12":
            voir_groupe(uid, user_info)
        elif choix == "0":
            print("[✓] Déconnexion réussie.")
            break
        else:
            print("[!] Option invalide.")


# ──────────────────────────────────────────────
#  Tableau de bord
# ──────────────────────────────────────────────

def _afficher_resume_etudiant(uid, user_info):
    """Affiche un petit résumé de l'emploi du temps de l'étudiant."""
    mes_ids = _mes_event_ids(uid, user_info)
    mes_events = [ev for ev in data.evenements if ev["id"] in mes_ids]
    today = date.today().isoformat()
    upcoming = [ev for ev in mes_events if ev.get("date", "") >= today]
    upcoming_sorted = sorted(upcoming, key=lambda x: (x.get("date", ""), x.get("heure", "")))
    prochain = upcoming_sorted[0] if upcoming_sorted else None

    nb_entretiens = sum(1 for ev in upcoming if ev.get("type") == "entretien")
    nb_deadlines = sum(1 for ev in upcoming if ev.get("type") == "deadline")

    print("\n─── Résumé étudiant ───")
    print(f"  Groupe              : {user_info.get('groupe', '—') or '—'}")
    print(f"  Événements à venir  : {len(upcoming)}")
    print(f"  Entretiens à venir  : {nb_entretiens}")
    print(f"  Deadlines à venir   : {nb_deadlines}")
    if prochain:
        print(f"  Prochain événement  : {prochain['date']} {prochain['heure']} — {prochain['titre']}")
    else:
        print("  Prochain événement  : aucun")


# ──────────────────────────────────────────────
#  Profil
# ──────────────────────────────────────────────

def afficher_profil(uid, info):
    print("\n─── Mon profil ───")
    print(f"  ID      : {uid}")
    print(f"  Nom     : {info['nom']}")
    print(f"  Email   : {info['email']}")
    print(f"  École   : {info.get('ecole', '—')}")
    print(f"  Groupe  : {info.get('groupe', '—')}")


def modifier_profil(uid, info):
    print("\n─── Modifier mon profil ───")
    print("Laissez vide pour conserver la valeur actuelle.")

    nom = input(f"Nom [{info.get('nom', '')}] : ").strip()
    if nom:
        info["nom"] = nom

    email = input(f"Email [{info.get('email', '')}] : ").strip()
    if email:
        if not _email_valide(email):
            print("[!] Email invalide. Modification annulée pour l'email.")
        elif _email_utilise_par_autre(email, uid):
            print("[!] Cet email est déjà utilisé par un autre compte.")
        else:
            if email.lower() != info.get("email", "").lower():
                info["email"] = email
                info["email_verified"] = False
                info["verification_code"] = None
                print("[!] Email modifié : vous devrez le revérifier à la prochaine connexion.")

    password = input("Nouveau mot de passe (laisser vide pour conserver) : ").strip()
    if password:
        confirmation = input("Confirmer le nouveau mot de passe : ").strip()
        if confirmation != password:
            print("[!] Confirmation incorrecte. Mot de passe non modifié.")
        else:
            info["password"] = password

    ecole = input(f"École [{info.get('ecole', '')}] : ").strip()
    if ecole:
        info["ecole"] = ecole

    data.save()
    print("[✓] Profil mis à jour.")


# ──────────────────────────────────────────────
#  Groupe collaboratif
# ──────────────────────────────────────────────

def voir_groupe(uid, user_info):
    """Affiche le groupe de l'étudiant et les événements partagés."""
    groupe = next(
        (g for g in data.groupes if uid in g.get("membres", [])), None
    )
    if not groupe:
        print("  Vous n'êtes membre d'aucun groupe collaboratif.")
        return

    print(f"\n─── Groupe : {groupe['nom']} ───")
    print("  Membres :")
    for etu in data.etudiants:
        if etu["id"] in groupe.get("membres", []):
            print(f"    • {etu['nom']} ({etu['email']})")

    print("\n  Événements du groupe :")
    ev_groupe = [e for e in data.evenements if e.get("groupe") == groupe["nom"]]
    if not ev_groupe:
        print("    (Aucun événement de groupe)")
        return
    for ev in sorted(ev_groupe, key=lambda x: (x["date"], x["heure"])):
        print(f"    [{ev['date']} {ev['heure']}] {ev['titre']} — {ev['type']}")


# ──────────────────────────────────────────────
#  Helpers
# ──────────────────────────────────────────────

def _mes_event_ids(uid, user_info):
    """
    Retourne les IDs des événements visibles par cet étudiant :
    - Événements qu'il a créés
    - Événements partagés avec lui
    - Événements de son groupe
    """
    ids = set()
    groupe_nom = user_info.get("groupe")
    for ev in data.evenements:
        if ev["createur_role"] == "etudiant" and ev["createur_id"] == uid:
            ids.add(ev["id"])
        elif uid in ev.get("partage_avec", []):
            ids.add(ev["id"])
        elif groupe_nom and ev.get("groupe") == groupe_nom:
            ids.add(ev["id"])
    return ids


def _email_valide(email):
    """Vérifie rapidement si le format d'un email est acceptable."""
    return re.match(EMAIL_REGEX, email) is not None


def _email_utilise_par_autre(email, uid):
    """Vérifie si l'email est déjà utilisé par un autre utilisateur."""
    email = email.lower()
    for liste in [data.administrateurs, data.etudiants, data.entreprises]:
        for user in liste:
            if user.get("email", "").lower() == email and user.get("id") != uid:
                return True
    return False
