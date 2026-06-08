from django.db import models


class Administrateur(models.Model):
    id = models.BigAutoField(primary_key=True)
    nom = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)

    def __str__(self):
        return self.nom


class Ecole(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    ville = models.CharField(max_length=100, blank=True)

    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)

    verified = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    verification_code = models.CharField(
        max_length=10,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.nom


class Groupe(models.Model):
    id = models.BigAutoField(primary_key=True)
    nom = models.CharField(max_length=50)
    ecole = models.ForeignKey(
        Ecole,
        on_delete=models.CASCADE,
        related_name="groupes",
    )

    def __str__(self):
        return f"{self.nom} - {self.ecole.nom}"


class Etudiant(models.Model):
    id = models.BigAutoField(primary_key=True)
    nom = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)

    ecole = models.ForeignKey(
        Ecole,
        on_delete=models.CASCADE,
        related_name="etudiants",
    )
    groupe = models.ForeignKey(
        Groupe,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="etudiants",
    )

    email_verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return self.nom


class Entreprise(models.Model):
    id = models.BigAutoField(primary_key=True)
    nom = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    secteur = models.CharField(max_length=100, blank=True)

    verified = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return self.nom


class EquipeStage(models.Model):
    id = models.BigAutoField(primary_key=True)
    nom = models.CharField(max_length=100)
    entreprise = models.ForeignKey(
        Entreprise,
        on_delete=models.CASCADE,
        related_name="equipes_stage",
    )
    etudiants = models.ManyToManyField(
        Etudiant,
        blank=True,
        related_name="equipes_stage",
    )

    def __str__(self):
        return f"{self.nom} - {self.entreprise.nom}"


class Evenement(models.Model):
    id = models.BigAutoField(primary_key=True)

    TYPE_CHOICES = [
        ("reunion", "Réunion"),
        ("entretien", "Entretien"),
        ("deadline", "Deadline"),
        ("autre", "Autre"),
    ]

    ROLE_CHOICES = [
        ("admin", "Administrateur"),
        ("etudiant", "Étudiant"),
        ("entreprise", "Entreprise"),
        ("ecole", "École"),
    ]

    STATUT_CHOICES = [
        ("planifie", "Planifié"),
        ("en_cours", "En cours"),
        ("termine", "Terminé"),
        ("annule", "Annulé"),
    ]

    titre = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    date = models.DateField()
    heure = models.TimeField()
    lieu = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)

    createur_role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    createur_id = models.IntegerField()

    ecoles = models.ManyToManyField(Ecole, blank=True, related_name="evenements")
    groupes = models.ManyToManyField(Groupe, blank=True, related_name="evenements") 
    etudiants = models.ManyToManyField(Etudiant, blank=True, related_name="evenements") 
    entreprises = models.ManyToManyField(Entreprise, blank=True, related_name="evenements") 
    equipes_stage = models.ManyToManyField(EquipeStage, blank=True, related_name="evenements") 

    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOICES,
        default="planifie",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.titre