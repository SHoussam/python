# ============================================================
#  admin.py — Fonctions Administrateur
#  StageLink · Gestionnaire d'emploi du temps collaboratif
# ============================================================

import re

import data
import evenements as ev_mod
from authentification import _get_all_users_of, _email_exists


EMAIL_PATTERN = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


def menu_admin(uid, user_info):
    """Menu principal de l'administrateur."""
    while True:
        _afficher_resume_admin()
        print("\n╔══════════════════════════════════════╗")
        print("║       MENU ADMINISTRATEUR            ║")
        print("╠══════════════════════════════════════╣")
        print("║  — Gestion des utilisateurs —        ║")
        print("║  1. Lister tous les utilisateurs     ║")
        print("║  2. Ajouter un utilisateur           ║")
        print("║  3. Modifier un utilisateur          ║")
        print("║  4. Supprimer un utilisateur         ║")
        print("║  5. Rechercher un utilisateur        ║")
        print("║  6. Vérifier une entreprise          ║")
        print("║  — Emploi du temps —                 ║")
        print("║  7. Voir tous les événements         ║")
        print("║  8. Créer un événement               ║")
        print("║  9. Modifier un événement            ║")
        print("║ 10. Supprimer un événement           ║")
        print("║ 11. Voir les disponibilités          ║")
        print("║ 12. Filtrer par type                 ║")
        print("║  — Groupes —                         ║")
        print("║ 13. Gérer les groupes                ║")
        print("╠══════════════════════════════════════╣")
        print("║  0. Déconnexion                      ║")
        print("╚══════════════════════════════════════╝")

        choix = input("Votre choix : ").strip()

        if choix == "1":
            lister_utilisateurs()
        elif choix == "2":
            ajouter_utilisateur()
        elif choix == "3":
            modifier_utilisateur()
        elif choix == "4":
            supprimer_utilisateur(uid)
        elif choix == "5":
            rechercher_utilisateur()
        elif choix == "6":
            verifier_entreprise()
        elif choix == "7":
            ev_mod.afficher_tous()
        elif choix == "8":
            ev_mod.creer_evenement("admin", uid)
        elif choix == "9":
            ev_mod.modifier_evenement("admin", uid)
        elif choix == "10":
            ev_mod.supprimer_evenement("admin", uid)
        elif choix == "11":
            ev_mod.voir_disponibilites()
        elif choix == "12":
            _filtrer_par_type()
        elif choix == "13":
            gerer_groupes(uid)
        elif choix == "0":
            print("[✓] Déconnexion réussie.")
            break
        else:
            print("[!] Option invalide.")


# ──────────────────────────────────────────────
#  Gestion des utilisateurs
# ──────────────────────────────────────────────

def lister_utilisateurs():
    print("\n─── Liste des utilisateurs ───")
    for role, liste in [
        ("Admin", data.administrateurs),
        ("Étudiant", data.etudiants),
        ("Entreprise", data.entreprises),
    ]:
        print(f"\n  [{role}s]")
        users = _get_all_users_of(liste)
        if not users:
            print("    (Aucun)")
        for uid, info in users:
            statut = ""
            if role == "Entreprise":
                statut = "✓ vérifié" if info.get("verified") else "⏳ en attente"
            print(f"    ID={uid} | {info['nom']} | {info['email']} {statut}")


def ajouter_utilisateur():
    print("\n─── Ajouter un utilisateur ───")
    print("  1. Administrateur  2. Étudiant  3. Entreprise")
    choix = input("Type : ").strip()
    nom = input("Nom : ").strip()
    email = input("Email : ").strip()
    passwd = input("Mot de passe : ").strip()

    if not nom or not email or not passwd:
        print("[!] Tous les champs principaux sont obligatoires.")
        return

    if not _email_valide(email):
        print("[!] Format d'email invalide.")
        return

    if _email_exists(email):
        print("[!] Cet email est déjà utilisé.")
        return

    if choix == "1":
        nid = data.next_ids["administrateurs"]
        data.administrateurs.append({
            "id": nid,
            "nom": nom,
            "email": email,
            "password": passwd,
        })
        data.next_ids["administrateurs"] += 1

    elif choix == "2":
        ecole = input("École : ").strip()
        groupe = input("Groupe : ").strip()
        nid = data.next_ids["etudiants"]
        data.etudiants.append({
            "id": nid,
            "nom": nom,
            "email": email,
            "password": passwd,
            "ecole": ecole,
            "groupe": groupe,
        })
        data.next_ids["etudiants"] += 1

        if groupe:
            groupe_obj = next((g for g in data.groupes if g["nom"] == groupe), None)
            if groupe_obj and nid not in groupe_obj["membres"]:
                groupe_obj["membres"].append(nid)

    elif choix == "3":
        secteur = input("Secteur : ").strip()
        verified_input = input("Entreprise vérifiée ? (o/n, vide = non) : ").strip().lower()
        nid = data.next_ids["entreprises"]
        data.entreprises.append({
            "id": nid,
            "nom": nom,
            "email": email,
            "password": passwd,
            "secteur": secteur,
            "verified": verified_input in ("o", "oui", "y", "yes", "1"),
        })
        data.next_ids["entreprises"] += 1

    else:
        print("[!] Choix invalide.")
        return

    data.save()
    print(f"[✓] Utilisateur ajouté (ID={nid}).")


def modifier_utilisateur():
    print("\n─── Modifier un utilisateur ───")
    role_str = input("Rôle (admin/etudiant/entreprise) : ").strip().lower()
    liste = _get_liste(role_str)
    if liste is None:
        return

    try:
        uid = int(input("ID : ").strip())
    except ValueError:
        print("[!] ID invalide.")
        return

    info = _trouver_user(liste, uid)
    if not info:
        return

    print("Laissez vide pour conserver.")

    nouveau_nom = input(f"Nom [{info['nom']}] : ").strip()
    nouvel_email = input(f"Email [{info['email']}] : ").strip()
    nouveau_mdp = input(f"Mot de passe [{info['password']}] : ").strip()

    if nouveau_nom:
        info["nom"] = nouveau_nom

    if nouvel_email:
        if not _email_valide(nouvel_email):
            print("[!] Format d'email invalide.")
            return
        email_deja_pris = any(
            user["email"].lower() == nouvel_email.lower() and user["id"] != uid
            for user in (data.administrateurs + data.etudiants + data.entreprises)
        )
        if email_deja_pris:
            print("[!] Cet email est déjà utilisé par un autre compte.")
            return
        info["email"] = nouvel_email

    if nouveau_mdp:
        info["password"] = nouveau_mdp

    if role_str == "etudiant":
        nouvelle_ecole = input(f"École [{info.get('ecole', '')}] : ").strip()
        nouveau_groupe = input(f"Groupe [{info.get('groupe', '')}] : ").strip()

        if nouvelle_ecole:
            info["ecole"] = nouvelle_ecole

        if nouveau_groupe:
            _retirer_etudiant_de_tous_les_groupes(uid)
            info["groupe"] = nouveau_groupe
            groupe_obj = next((g for g in data.groupes if g["nom"] == nouveau_groupe), None)
            if groupe_obj and uid not in groupe_obj["membres"]:
                groupe_obj["membres"].append(uid)
        elif nouveau_groupe == "":
            pass

    elif role_str == "entreprise":
        nouveau_secteur = input(f"Secteur [{info.get('secteur', '')}] : ").strip()
        verification = input(
            f"Vérifiée [{ 'oui' if info.get('verified') else 'non' }] (o/n ou vide) : "
        ).strip().lower()

        if nouveau_secteur:
            info["secteur"] = nouveau_secteur
        if verification in ("o", "oui", "y", "yes", "1"):
            info["verified"] = True
        elif verification in ("n", "non", "no", "0"):
            info["verified"] = False

    data.save()
    print("[✓] Utilisateur modifié.")


def supprimer_utilisateur(admin_uid):
    print("\n─── Supprimer un utilisateur ───")
    role_str = input("Rôle (admin/etudiant/entreprise) : ").strip().lower()
    liste = _get_liste(role_str)
    if liste is None:
        return

    try:
        uid = int(input("ID : ").strip())
    except ValueError:
        print("[!] ID invalide.")
        return

    user = _trouver_user(liste, uid)
    if not user:
        return

    if role_str == "admin":
        if uid == admin_uid:
            print("[!] Vous ne pouvez pas supprimer votre propre compte pendant cette session.")
            return
        if len(data.administrateurs) == 1:
            print("[!] Impossible de supprimer le dernier administrateur.")
            return

    confirmation = input(f"Confirmer la suppression de '{user['nom']}' ? (o/n) : ").strip().lower()
    if confirmation not in ("o", "oui", "y", "yes"):
        print("  Suppression annulée.")
        return

    if role_str == "etudiant":
        _nettoyer_references_etudiant(uid)
    elif role_str == "entreprise":
        _supprimer_evenements_entreprise(uid)

    liste.remove(user)
    data.save()
    print(f"[✓] Utilisateur ID={uid} supprimé.")


def rechercher_utilisateur():
    mot = input("Nom ou email à rechercher : ").strip().lower()
    trouve = False
    for role, liste in [
        ("Admin", data.administrateurs),
        ("Étudiant", data.etudiants),
        ("Entreprise", data.entreprises),
    ]:
        for uid, info in _get_all_users_of(liste):
            if mot in info["nom"].lower() or mot in info["email"].lower():
                print(f"  [{role}] ID={uid} | {info['nom']} | {info['email']}")
                trouve = True
    if not trouve:
        print("  (Aucun résultat)")


def verifier_entreprise():
    print("\n─── Vérification d'entreprise ───")
    non_verifiees = [
        (uid, info)
        for uid, info in _get_all_users_of(data.entreprises)
        if not info.get("verified")
    ]
    if not non_verifiees:
        print("  Aucune entreprise en attente de vérification.")
        return

    for uid, info in non_verifiees:
        print(f"  ID={uid} | {info['nom']} | {info.get('secteur', '—')}")

    try:
        uid = int(input("ID de l'entreprise à vérifier : ").strip())
    except ValueError:
        print("[!] ID invalide.")
        return

    info = _trouver_user(data.entreprises, uid)
    if info:
        info["verified"] = True
        data.save()
        print(f"[✓] Entreprise ID={uid} vérifiée.")


# ──────────────────────────────────────────────
#  Groupes
# ──────────────────────────────────────────────

def gerer_groupes(admin_uid):
    while True:
        print("\n─── Gestion des groupes ───")
        print("  1. Lister les groupes")
        print("  2. Créer un groupe")
        print("  3. Ajouter un membre")
        print("  4. Retirer un membre")
        print("  0. Retour")
        choix = input("Choix : ").strip()

        if choix == "1":
            _lister_groupes()
        elif choix == "2":
            _creer_groupe(admin_uid)
        elif choix == "3":
            _ajouter_membre()
        elif choix == "4":
            _retirer_membre()
        elif choix == "0":
            break
        else:
            print("[!] Option invalide.")


def _lister_groupes():
    if not data.groupes:
        print("  (Aucun groupe)")
        return

    for g in data.groupes:
        membres_noms = []
        for uid, info in _get_all_users_of(data.etudiants):
            if uid in g["membres"]:
                membres_noms.append(info["nom"])
        print(
            f"  Groupe '{g['nom']}' (ID={g['id']}) — membres : "
            f"{', '.join(membres_noms) or 'aucun'}"
        )


def _creer_groupe(admin_uid):
    nom = input("Nom du groupe : ").strip()
    if not nom:
        print("[!] Le nom du groupe est obligatoire.")
        return

    if any(g["nom"].lower() == nom.lower() for g in data.groupes):
        print("[!] Un groupe avec ce nom existe déjà.")
        return

    nid = data.next_ids["groupes"]
    data.groupes.append({"id": nid, "nom": nom, "membres": [], "admin_id": admin_uid})
    data.next_ids["groupes"] += 1
    data.save()
    print(f"[✓] Groupe '{nom}' créé (ID={nid}).")


def _ajouter_membre():
    try:
        gid = int(input("ID du groupe : ").strip())
        uid = int(input("ID de l'étudiant : ").strip())
    except ValueError:
        print("[!] ID invalide.")
        return

    groupe = next((g for g in data.groupes if g["id"] == gid), None)
    if not groupe:
        print("[!] Groupe introuvable.")
        return

    etudiant = _trouver_user(data.etudiants, uid)
    if not etudiant:
        return

    if uid in groupe["membres"]:
        print("  (Déjà membre)")
        return

    _retirer_etudiant_de_tous_les_groupes(uid)
    groupe["membres"].append(uid)
    etudiant["groupe"] = groupe["nom"]
    data.save()
    print(f"[✓] Étudiant ID={uid} ajouté au groupe '{groupe['nom']}'.")


def _retirer_membre():
    try:
        gid = int(input("ID du groupe : ").strip())
        uid = int(input("ID de l'étudiant : ").strip())
    except ValueError:
        print("[!] ID invalide.")
        return

    groupe = next((g for g in data.groupes if g["id"] == gid), None)
    if not groupe:
        print("[!] Groupe introuvable.")
        return

    if uid not in groupe["membres"]:
        print("[!] Cet étudiant n'est pas membre.")
        return

    groupe["membres"].remove(uid)
    etudiant = _trouver_user(data.etudiants, uid)
    if etudiant and etudiant.get("groupe") == groupe["nom"]:
        etudiant["groupe"] = ""

    data.save()
    print(f"[✓] Étudiant ID={uid} retiré du groupe.")


# ──────────────────────────────────────────────
#  Helpers internes
# ──────────────────────────────────────────────

def _afficher_resume_admin():
    non_verifiees = sum(1 for e in data.entreprises if not e.get("verified"))
    print("\n─── Résumé admin ───")
    print(f"  Admins         : {len(data.administrateurs)}")
    print(f"  Étudiants      : {len(data.etudiants)}")
    print(f"  Entreprises    : {len(data.entreprises)}")
    print(f"  Non vérifiées  : {non_verifiees}")
    print(f"  Événements     : {len(data.evenements)}")
    print(f"  Groupes        : {len(data.groupes)}")


def _filtrer_par_type():
    print("Types : entretien, reunion, deadline, validation, cours")
    t = input("Type : ").strip().lower()
    ev_mod.afficher_par_type(t)


def _get_liste(role_str):
    mapping = {
        "admin": data.administrateurs,
        "etudiant": data.etudiants,
        "entreprise": data.entreprises,
    }
    liste = mapping.get(role_str)
    if liste is None:
        print("[!] Rôle invalide.")
    return liste


def _trouver_user(liste, uid):
    for user in liste:
        if user["id"] == uid:
            return user
    print(f"[!] Utilisateur ID={uid} introuvable.")
    return None


def _email_valide(email):
    return re.match(EMAIL_PATTERN, email) is not None


def _retirer_etudiant_de_tous_les_groupes(uid):
    for groupe in data.groupes:
        if uid in groupe["membres"]:
            groupe["membres"].remove(uid)


def _nettoyer_references_etudiant(uid):
    _retirer_etudiant_de_tous_les_groupes(uid)

    for ev in data.evenements:
        if uid in ev.get("partage_avec", []):
            ev["partage_avec"].remove(uid)

    data.evenements[:] = [
        ev for ev in data.evenements
        if not (ev.get("createur_role") == "etudiant" and ev.get("createur_id") == uid)
    ]


def _supprimer_evenements_entreprise(uid):
    avant = len(data.evenements)
    data.evenements[:] = [
        ev for ev in data.evenements
        if not (ev.get("createur_role") == "entreprise" and ev.get("createur_id") == uid)
    ]
    supprimes = avant - len(data.evenements)
    if supprimes:
        print(f"  {supprimes} événement(s) de l'entreprise ont aussi été supprimé(s).")
