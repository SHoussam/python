# StageLink 👨‍🎓👩‍💼📅

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**StageLink** est un **gestionnaire d'emploi du temps collaboratif** conçu pour les stages et entretiens d'embauche. 
Développé pour le **Mini-Projet Python — 3ème année IIR** à l'**EMSI Tanger (2025/2026)**.

```
╔══════════════════════════════════════════════════════════╗
║   ███████╗████████╗ █████╗  ██████╗ ███████╗            ║
║   L I N K  ── Gestionnaire d'emploi du temps            ║
║            ── Suivi de stage collaboratif               ║
╚══════════════════════════════════════════════════════════╝
```

## ✨ Fonctionnalités

### 👥 **Multi-rôles**
- **Admin** : Gestion complète (utilisateurs, événements, groupes)
- **Étudiant** : Profil, emploi du temps personnel/groupe, création d'événements
- **Entreprise** : Planification d'entretiens, invitation d'étudiants, vérification disponibilités

### 📅 **Gestion d'événements avancée**
- Types : `entretien`, `reunion`, `deadline`, `validation`, `cours`
- Partage individuel (inviter étudiants spécifiques) ou par groupe
- **Détection automatique de conflits** (même date/heure)
- CRUD complet (créer/voir/modifier/supprimer/rechercher)
- Filtrage par type, disponibilités par date

### 🛡️ **Sécurité & Authentification**
- Inscription avec **vérification email** (SMTP configurable)
- Connexion sécurisée (3 tentatives max)
- Vérification admin pour entreprises
- Validation des inputs (email, date/heure, etc.)

### 💾 **Persistance**
- Stockage JSON automatique (`data.json`)
- Sauvegarde à chaque modification / sortie propre
- Gestion des erreurs (fichier manquant/corrompu)

### 👥 **Groupes collaboratifs**
- Création/gestion par admin
- Ajout/retrait d'étudiants
- Événements partagés au groupe entier

## 🗂️ Structure du projet

```
.
├── main.py                 # Point d'entrée & menu principal
├── data.py                 # Structures de données globales
├── storage.py              # Persistance JSON
├── authentification.py     # Inscription/connexion/email
├── admin.py                # Panneau admin complet
├── etudiant.py             # Interface étudiant
├── entreprise.py           # Interface entreprise
├── evenements.py           # CRUD événements partagé
├── data.json               # Base de données (auto-générée)
├── README.md               # 📄 Ce fichier
```

## 🚀 Installation & Démarrage

1. **Clonez/Téléchargez** le projet
2. **Python 3.8+** requis (stdlib uniquement)
3. **Configuration email** (optionnel, pour vérification) :
   ```bash
   # Windows (PowerShell)
   $env:STAGELINK_SMTP_SERVER="smtp.gmail.com"
   $env:STAGELINK_SMTP_PORT="465"
   $env:STAGELINK_SMTP_EMAIL="votre.email@gmail.com"
   $env:STAGELINK_SMTP_PASSWORD="votre-app-password"

   # Linux/Mac
   export STAGELINK_SMTP_SERVER="smtp.gmail.com"
   export STAGELINK_SMTP_PORT="465"
   export STAGELINK_SMTP_EMAIL="votre.email@gmail.com"
   export STAGELINK_SMTP_PASSWORD="votre-app-password"
   ```
4. **Lancez** :
   ```bash
   python main.py
   ```

## 📱 Capture d'écran (CLI)

```
===== MENU PRINCIPAL =====
  1. Se connecter
  2. S'inscrire  
  0. Quitter
Votre choix : 
```

**Admin Dashboard** :
```
─── Résumé admin ───
  Admins         : 1
  Étudiants      : 5
  Entreprises    : 2
  Non vérifiées  : 1
  Événements     : 3
  Groupes        : 1
```

## 🗄️ Modèle de données (data.json)

```json
{
  "administrateurs": [{"id":1,"nom":"Admin","email":"admin@emsi.ma","password":"pass"}],
  "etudiants": [{"id":1,"nom":"Etudiant","email":"etu@emsi.ma","ecole":"EMSI","groupe":"GroupeA"}],
  "entreprises": [{"id":1,"nom":"EntrepriseX","email":"rh@entreprise.com","verified":true}],
  "evenements": [{
    "id":1,"titre":"Entretien Stage","type":"entretien","date":"2025-01-15",
    "heure":"14:00","lieu":"Zoom","createur_role":"entreprise","createur_id":1,
    "partage_avec":[1,2],"groupe":null
  }],
  "groupes": [{"id":1,"nom":"GroupeA","membres":[1,2]}],
  "next_ids": {"administrateurs":2,"etudiants":2,...}
}
```

## 👨‍💼 Utilisation typique

1. **Admin** : Crée étudiants/entreprises, vérifie entreprises, gère groupes/événements
2. **Étudiant** : S'inscrit, vérifie email, voit emploi du temps, crée rappels deadlines
3. **Entreprise** : S'inscrit → vérif admin → planifie entretiens → invite étudiants

## 🔧 Admin - Tâches importantes

```
1. Lister/Ajouter/Modifier/Supprimer utilisateurs
6. Vérifier une entreprise ← CRITIQUE
7. Voir/Créer/Modifier/Supprimer événements
13. Gérer les groupes
```

## 🚀 Améliorations futures

- [ ] Interface web (Flask/FastAPI)
- [ ] Notifications push (email/SMS)
- [ ] Calendrier iCal/Google Calendar export
- [ ] Dashboard analytics (stats entretiens)
- [ ] Upload CV/portfolios
- [ ] Matching IA étudiants/offres

## 🐛 Dépannage

- **Email non envoyé** : Vérifiez variables d'environnement SMTP
- **data.json corrompu** : Supprimez-le (re-créé vide)
- **Pas d'admin** : Ajoutez manuellement dans data.json ou via menu admin

## 📄 Licence

MIT License - Voir [LICENSE](LICENSE) (à créer)

---

**Développé avec ❤️ pour EMSI Tanger**  
*Mise à jour : `date`**  
*Generated by BLACKBOXAI*
