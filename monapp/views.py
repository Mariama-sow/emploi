from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from collections import defaultdict
from django.contrib import messages
from .models import Classe, Departement, ElementDeModule, NonDisponibilite, Enseignant , Etudiant , CoursClasse
from .forms import NonDisponibiliteForm

def is_enseignant(user):
    return user.is_authenticated and user.role == 'enseignant'

@login_required
@user_passes_test(is_enseignant)
def enseignant_dashboard(request):
    enseignant = get_object_or_404(Enseignant, user=request.user)
    
    # Récupérer tous les cours de l'enseignant
    cours = ElementDeModule.objects.filter(enseignant=enseignant).order_by('jour', 'heureDebut')
    
    # Grouper les cours par matière, jour et classe
    cours_details = {}
    for cours_item in cours:
        jour = cours_item.jour
        if jour not in cours_details:
            cours_details[jour] = []
        
        cours_details[jour].append({
            'matiere': cours_item.matiere,
            'classe': cours_item.classes.first().nom_classe if cours_item.classes.exists() else 'N/A',
            'heure_debut': cours_item.heureDebut,
            'heure_fin': cours_item.heureFin,
            'salle': cours_item.salle.numSalle if cours_item.salle else 'Non attribuée',
        })
    
    # Récupérer les non-disponibilités
    non_disponibilites = NonDisponibilite.objects.filter(enseignant=enseignant)
    
    context = {
        'enseignant': enseignant,
        'cours_details': cours_details,
        'non_disponibilites': non_disponibilites,
    }
    return render(request, 'accounts/teacher_dashboard.html', context)
@login_required
@user_passes_test(is_enseignant)
def ajouter_non_disponibilite(request):
    try:
        enseignant = Enseignant.objects.get(user=request.user)
    except Enseignant.DoesNotExist:
        messages.error(request, "Aucun profil enseignant associé à cet utilisateur.")
        return redirect('enseignant_dashboard')  

    if request.method == 'POST':
        form = NonDisponibiliteForm(request.POST)
        if form.is_valid():
            non_dispo = form.save(commit=False)
            non_dispo.enseignant = enseignant  # ✅ Associer l'enseignant ici
            non_dispo.full_clean()  # ✅ `enseignant_id` sera disponible dans `clean()`
            non_dispo.save()
            messages.success(request, 'Non-disponibilité ajoutée avec succès.')
            return redirect('enseignant_dashboard')
        else:
            print(form.errors)  # 🔍 Afficher les erreurs du formulaire pour debug
    else:
        form = NonDisponibiliteForm()

    return render(request, 'monapp/ajouter_non_disponibilite.html', {'form': form})


@login_required
@user_passes_test(is_enseignant)
def supprimer_non_disponibilite(request, pk):
    non_dispo = get_object_or_404(NonDisponibilite, pk=pk, enseignant__user=request.user)
    
    if request.method == 'POST':
        non_dispo.delete()
        messages.success(request, 'Non-disponibilité supprimée avec succès.')
        return redirect('enseignant_dashboard')
    
    return render(request, 'monapp/confirmer_suppression.html', {'objet': non_dispo})




def is_etudiant(user):
    return user.is_authenticated and user.role == 'etudiant'

@login_required
@user_passes_test(is_etudiant)
def etudiant_dashboard(request):
    etudiant = request.user.etudiant
    classe = etudiant.classe

    # Définir les heures de 8h à 18h
    heures = range(8, 19)  
    jours = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi']

    # Récupérer les cours de la classe avec plus de détails
    if classe:
        # Utiliser la relation many-to-many via CoursClasse
        cours_list = ElementDeModule.objects.filter(
            classes=classe
        ).distinct().order_by('jour', 'heureDebut')
    else:
        cours_list = ElementDeModule.objects.none()

    # Organiser les cours par jour avec des informations détaillées
    cours_par_jour = {}
    for jour in jours:
        cours_du_jour = cours_list.filter(jour=jour)
        cours_par_jour[jour] = []
        
        for cours in cours_du_jour:
            # Récupérer l'enseignant et la salle
            cours_details = {
                'matiere': cours.matiere,
                'enseignant': cours.enseignant,
                'salle': cours.salle,
                'heure_debut': cours.heureDebut,
                'heure_fin': cours.heureFin,
                'volume_horaire_session': cours.volumeHoraire
            }
            cours_par_jour[jour].append(cours_details)

    context = {
        'etudiant': etudiant,
        'cours': cours_par_jour,
        'jours': jours,
        'heures': heures,
    }
    return render(request, 'accounts/student_dashboard.html', context)

@login_required
@user_passes_test(is_etudiant)
def voir_emploi_temps(request):
    etudiant = get_object_or_404(Etudiant, user=request.user)
    classe = getattr(etudiant, 'classe', None)
    
    # Définir les heures de cours
    heures = range(8, 19)  # De 8h à 18h
    jours = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi']
    
    # Initialiser l'emploi du temps
    emploi_temps = {jour: [] for jour in jours}
    
    if classe:
        # Récupérer les cours de la classe
        cours = ElementDeModule.objects.filter(
            classes=classe
        ).order_by('jour', 'heureDebut')
        
        # Organiser les cours par jour
        for c in cours:
            emploi_temps[c.jour].append({
                'matiere': c.matiere,
                'enseignant': c.enseignant,
                'salle': c.salle,
                'heure_debut': c.heureDebut,
                'heure_fin': c.heureFin,
                'volume_horaire_session': c.volumeHoraire
            })

    return render(request, 'monapp/emploi_temps.html', {
        'emploi_temps': emploi_temps,
        'jours': jours,
        'classe': classe,
        'heures': heures
    })




def is_admin(user):
    return user.is_authenticated and user.is_superuser

@user_passes_test(is_admin)
def admin_dashboard(request):
    # Récupérer des données pour le tableau de bord de l'administrateur
    nombre_etudiants = Etudiant.objects.count()
    nombre_enseignants = Enseignant.objects.count()
    nombre_classes = Classe.objects.count()
    nombre_departements = Departement.objects.count()

    context = {
        'nombre_etudiants': nombre_etudiants,
        'nombre_enseignants': nombre_enseignants,
        'nombre_classes': nombre_classes,
        'nombre_departements': nombre_departements,
    }

    return render(request, 'account/admin_dashboard.html', context)