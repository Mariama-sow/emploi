from django.urls import path
from . import views

urlpatterns = [
    # URLs pour les enseignants
    path('enseignant/', views.enseignant_dashboard, name='enseignant_dashboard'),
    path('enseignant/non-disponibilite/ajouter/', views.ajouter_non_disponibilite, name='ajouter_non_disponibilite'),
    path('enseignant/non-disponibilite/supprimer/<int:pk>/', views.supprimer_non_disponibilite, name='supprimer_non_disponibilite'),
    
    # URLs pour les étudiants
    path('etudiant/', views.etudiant_dashboard, name='etudiant_dashboard'),
    path('emploi-temps/', views.voir_emploi_temps, name='voir_emploi_temps'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
]