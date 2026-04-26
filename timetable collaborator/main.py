#!/usr/bin/env python3
# ============================================================
#  main.py — Point d'entrée principal
#  StageLink · Gestionnaire d'emploi du temps collaboratif
#
#  Mini-Projet Python — 3ème année IIR
#  EMSI Tanger · 2025/2026
# ============================================================

import authentification as auth
import admin
import etudiant
import entreprise
import data


BANNER = """
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║   ███████╗████████╗ █████╗  ██████╗ ███████╗            ║
║   ██╔════╝╚══██╔══╝██╔══██╗██╔════╝ ██╔════╝            ║
║   ███████╗   ██║   ███████║██║  ███╗█████╗              ║
║   ╚════██║   ██║   ██╔══██║██║   ██║██╔══╝              ║
║   ███████║   ██║   ██║  ██║╚██████╔╝███████╗            ║
║   ╚══════╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚══════╝            ║
║                                                          ║
║   L I N K  ── Gestionnaire d'emploi du temps            ║
║            ── Suivi de stage collaboratif               ║
╚══════════════════════════════════════════════════════════╝
"""


def lancer_menu_role(role, uid, user_info):
    """Redirige l'utilisateur connecté vers le menu correspondant à son rôle."""
    if role == "admin":
        admin.menu_admin(uid, user_info)
    elif role == "etudiant":
        etudiant.menu_etudiant(uid, user_info)
    elif role == "entreprise":
        entreprise.menu_entreprise(uid, user_info)
    elif role is not None:
        print("[!] Rôle inconnu. Retour au menu principal.")


def menu_principal():
    """Affiche le menu principal et gère la navigation générale de l'application."""
    print(BANNER)

    while True:
        print("\n===== MENU PRINCIPAL =====")
        print("  1. Se connecter")
        print("  2. S'inscrire")
        print("  0. Quitter")
        choix = input("Votre choix : ").strip()

        if choix == "1":
            role, uid, user_info = auth.connexion()
            lancer_menu_role(role, uid, user_info)

        elif choix == "2":
            auth.inscription()

        elif choix == "0":
            data.save()
            print("\n  Au revoir ! À bientôt sur StageLink.\n")
            break

        else:
            print("[!] Option invalide.")


def main():
    """Lance l'application et sauvegarde les données même en cas d'arrêt clavier."""
    try:
        menu_principal()
    except KeyboardInterrupt:
        data.save()
        print("\n\n[!] Programme interrompu. Données sauvegardées.")


if __name__ == "__main__":
    main()
