from django.contrib import admin
from .models import (
    Administrateur,
    Ecole,
    Groupe,
    Etudiant,
    Entreprise,
    EquipeStage,
    Evenement,
)

admin.site.register(Administrateur)
admin.site.register(Ecole)
admin.site.register(Groupe)
admin.site.register(Etudiant)
admin.site.register(Entreprise)
admin.site.register(EquipeStage)
admin.site.register(Evenement)