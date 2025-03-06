# admin.py
from django.contrib import admin
from .models import (CustomUser, Etudiant, Enseignant, NonDisponibilite, 
                     Salle, ElementDeModule, Departement, Classe, Semestre,CoursClasse)
from django.contrib.auth.admin import UserAdmin

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'first_name', 'last_name', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Informations supplémentaires', {'fields': ('tel', 'role')}),
    )
    list_filter = ('role', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')

class EtudiantAdmin(admin.ModelAdmin):
    list_display = ('matricule', 'get_username', 'get_nom_prenom')
    search_fields = ('matricule', 'user__username', 'user__first_name', 'user__last_name')
    
    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Nom d\'utilisateur'
    
    def get_nom_prenom(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    get_nom_prenom.short_description = 'Nom et prénom'

class EnseignantAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'specialite', 'get_nom_prenom')
    search_fields = ('user__username', 'specialite', 'user__first_name', 'user__last_name')
    
    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Nom d\'utilisateur'
    
    def get_nom_prenom(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    get_nom_prenom.short_description = 'Nom et prénom'

class ElementDeModuleAdmin(admin.ModelAdmin):
    list_display = ('matiere', 'jour', 'heureDebut', 'heureFin', 'get_enseignant', 'get_salle')
    list_filter = ('jour', 'enseignant', 'salle')
    search_fields = ('matiere', 'enseignant__user__username', 'salle__numSalle')
    
    def get_enseignant(self, obj):
        return obj.enseignant.user.username
    get_enseignant.short_description = 'Enseignant'
    
    def get_salle(self, obj):
        return obj.salle.numSalle if obj.salle else "Non assignée"
    get_salle.short_description = 'Salle'


class CoursClasseAdmin(admin.ModelAdmin):
    list_display = ('cours', 'classe')
    list_filter = ('classe', 'cours')
    search_fields = ('cours__matiere', 'classe__nom_classe')

admin.site.register(CoursClasse, CoursClasseAdmin)

# Enregistrement des modèles
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Etudiant, EtudiantAdmin)
admin.site.register(Enseignant, EnseignantAdmin)
admin.site.register(NonDisponibilite)
admin.site.register(Salle)
admin.site.register(ElementDeModule, ElementDeModuleAdmin)
admin.site.register(Departement)
admin.site.register(Classe)
admin.site.register(Semestre)