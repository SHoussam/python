# ============================================================
#  authentification.py — Inscription & Connexion
#  StageLink · Gestionnaire d'emploi du temps collaboratif
# ============================================================

import os
import random
import re
import smtplib
import ssl
from email.mime.text import MIMEText

import data

SMTP_SERVER = os.getenv("STAGELINK_SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("STAGELINK_SMTP_PORT", "465"))
SMTP_EMAIL = os.getenv("STAGELINK_SMTP_EMAIL", "")
SMTP_PASSWORD = os.getenv("STAGELINK_SMTP_PASSWORD", "")


# ──────────────────────────────────────────────
#  Helpers
# ──────────────────────────────────────────────

def _get_all_users_of(liste):
    """Retourne une liste plate de (id, dict_user)."""
    return [(user["id"], user) for user in liste]



def _email_exists(email):
    """Vérifie si un email est déjà utilisé (toutes listes confondues)."""
    email = email.lower()
    for liste in [data.administrateurs, data.etudiants, data.entreprises]:
        for _, info in _get_all_users_of(liste):
            if info["email"].lower() == email:
                return True
    return False



def _is_valid_email(email):
    """Validation simple du format d'email."""
    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return re.match(pattern, email) is not None



def _generer_code_verification():
    """Génère un code numérique à 6 chiffres."""
    return f"{random.randint(0, 999999):06d}"



def _envoyer_email_verification(destinataire, nom, code):
    """Envoie le code de vérification par email via SMTP."""
    if not SMTP_EMAIL or not SMTP_PASSWORD:
        raise RuntimeError(
            "SMTP non configuré. Définissez STAGELINK_SMTP_EMAIL et STAGELINK_SMTP_PASSWORD."
        )

    sujet = "StageLink — Code de vérification"
    corps = (
        f"Bonjour {nom},\n\n"
        f"Bienvenue sur StageLink.\n"
        f"Votre code de vérification est : {code}\n\n"
        f"Saisissez ce code dans l'application pour activer votre compte.\n\n"
        f"Si vous n'êtes pas à l'origine de cette inscription, ignorez ce message.\n\n"
        f"— Équipe StageLink"
    )

    message = MIMEText(corps, _charset="utf-8")
    message["Subject"] = sujet
    message["From"] = SMTP_EMAIL
    message["To"] = destinataire

    context = ssl._create_unverified_context()
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as serveur:
        serveur.login(SMTP_EMAIL, SMTP_PASSWORD)
        serveur.sendmail(SMTP_EMAIL, [destinataire], message.as_string())



def _confirmer_code_utilisateur(utilisateur):
    """Demande le code reçu par email et valide le compte."""
    print("\n===== VÉRIFICATION EMAIL =====")
    for tentative in range(3):
        code_saisi = input("Entrez le code reçu par email : ").strip()
        if code_saisi == utilisateur.get("verification_code"):
            utilisateur["email_verified"] = True
            utilisateur["verification_code"] = None
            data.save()
            print("[✓] Email vérifié avec succès. Compte activé.")
            return True
        restantes = 2 - tentative
        if restantes >= 0:
            print(f"[!] Code incorrect. Tentatives restantes : {restantes}")
    print("[✗] Vérification échouée.")
    return False



def _envoyer_et_verifier_code(utilisateur):
    """Génère un code, l'envoie par email puis demande confirmation."""
    code = _generer_code_verification()
    utilisateur["verification_code"] = code
    utilisateur["email_verified"] = False
    data.save()

    try:
        _envoyer_email_verification(utilisateur["email"], utilisateur["nom"], code)
        print(f"[✓] Un code de vérification a été envoyé à {utilisateur['email']}.")
    except Exception as exc:
        print("[!] Impossible d'envoyer l'email de vérification.")
        print(f"    Détail : {exc}")
        print("    Configurez l'email SMTP puis reconnectez-vous pour renvoyer un code.")
        return False

    return _confirmer_code_utilisateur(utilisateur)


# ──────────────────────────────────────────────
#  Inscription
# ──────────────────────────────────────────────

def inscription():
    """Inscrit un nouvel utilisateur (étudiant ou entreprise)."""
    print("\n===== INSCRIPTION =====")
    print("Choisissez votre rôle :")
    print("  1. Étudiant")
    print("  2. Entreprise")
    choix = input("Votre choix : ").strip()

    if choix not in ("1", "2"):
        print("[!] Choix invalide. Retour au menu principal.")
        return

    nom = input("Nom complet / Raison sociale : ").strip()
    email = input("Email : ").strip()
    passwd = input("Mot de passe : ").strip()
    confirm = input("Confirmer le mot de passe : ").strip()

    if not nom or not email or not passwd or not confirm:
        print("[!] Tous les champs sont obligatoires.")
        return

    if not _is_valid_email(email):
        print("[!] Format d'email invalide.")
        return

    if passwd != confirm:
        print("[!] Les mots de passe ne correspondent pas.")
        return

    if _email_exists(email):
        print("[!] Cet email est déjà utilisé.")
        return

    utilisateur = None

    if choix == "1":
        ecole = input("École : ").strip()
        groupe = input("Groupe (ex: Groupe_A) : ").strip()
        nid = data.next_ids["etudiants"]
        utilisateur = {
            "id": nid,
            "nom": nom,
            "email": email,
            "password": passwd,
            "ecole": ecole,
            "groupe": groupe,
            "email_verified": False,
            "verification_code": None,
        }
        data.etudiants.append(utilisateur)
        data.next_ids["etudiants"] += 1
        data.save()
        print(f"[✓] Compte étudiant créé avec succès (ID={nid}).")

    else:
        secteur = input("Secteur d'activité : ").strip()
        nid = data.next_ids["entreprises"]
        utilisateur = {
            "id": nid,
            "nom": nom,
            "email": email,
            "password": passwd,
            "secteur": secteur,
            "verified": False,
            "email_verified": False,
            "verification_code": None,
        }
        data.entreprises.append(utilisateur)
        data.next_ids["entreprises"] += 1
        data.save()
        print(
            f"[✓] Compte entreprise créé (ID={nid}). En attente de vérification par l'admin."
        )

    _envoyer_et_verifier_code(utilisateur)


# ──────────────────────────────────────────────
#  Connexion
# ──────────────────────────────────────────────

def connexion():
    """
    Authentifie un utilisateur (max 3 tentatives).
    Retourne (role, id, dict_user) ou (None, None, None).
    """
    print("\n===== CONNEXION =====")
    tentatives = 0

    while tentatives < 3:
        email = input("Email : ").strip()
        passwd = input("Mot de passe : ").strip()

        for role, liste in [
            ("admin", data.administrateurs),
            ("etudiant", data.etudiants),
            ("entreprise", data.entreprises),
        ]:
            for uid, info in _get_all_users_of(liste):
                if info["email"].lower() == email.lower() and info["password"] == passwd:
                    if role != "admin" and not info.get("email_verified", True):
                        print("\n[!] Votre email n'est pas encore vérifié.")
                        reponse = input("Renvoyer un code maintenant ? (o/n) : ").strip().lower()
                        if reponse == "o":
                            if _envoyer_et_verifier_code(info):
                                print(f"\n[✓] Bienvenue, {info['nom']} ! (rôle : {role})")
                                return role, uid, info
                        return None, None, None

                    print(f"\n[✓] Bienvenue, {info['nom']} ! (rôle : {role})")
                    return role, uid, info

        tentatives += 1
        restantes = 3 - tentatives
        if restantes > 0:
            print(
                f"[!] Email ou mot de passe incorrect. Tentatives restantes : {restantes}"
            )
        else:
            print("[✗] Nombre maximum de tentatives atteint. Accès bloqué temporairement.")

    return None, None, None
