from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required 
from .decorators import etudiant_required , enseignant_required
from django.contrib import messages
from django.contrib.auth import login , logout
from django.views.generic import CreateView
from django.urls import reverse_lazy
from .forms import UserRegistrationForm , LoginForm
from django.contrib.auth import authenticate
from monapp.models import Classe, Departement, Etudiant , Enseignant
from .models import CustomUser

 
def home(request):
    return render(request, 'accounts/home.html')

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Bienvenue {username}!')
                # Redirection selon le rôle
                if user.role == 'etudiant':
                    return redirect('etudiant_dashboard')
                elif user.role == 'enseignant':
                    return redirect('enseignant_dashboard')
                else:
                    return redirect('admin_dashboard')
            else:
                messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Créer l'utilisateur
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            # Créer le profil correspondant selon le rôle
            if user.role == 'etudiant':
                Etudiant.objects.create(
                    user=user,
                    matricule=form.cleaned_data['matricule'],
                    classe=form.cleaned_data['classe']
                )
            elif user.role == 'enseignant':
                Enseignant.objects.create(
                    user=user,
                    specialite=form.cleaned_data['specialite']
                )
            
            # Connecter l'utilisateur
            login(request, user)
            messages.success(request, 'Votre compte a été créé avec succès!')
            
            # Rediriger selon le rôle
            if user.role == 'etudiant':
                return redirect('etudiant_dashboard')
            elif user.role == 'enseignant':
                return redirect('enseignant_dashboard')
        else:
            # Afficher les erreurs de validation
            print("Erreurs de formulaire:", form.errors)
    else:
        form = UserRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})
# Vue de tableau de bord pour les étudiants

# @login_required
# @etudiant_required
# def student_dashboard(request):
#     student = Etudiant.objects.get(user=request.user)
    
#     return render(request, 'accounts/student_dashboard.html', {
#         'student': student,
#     })

# # Vue de tableau de bord pour les enseignants
# @login_required
# @enseignant_required
# def teacher_dashboard(request):
#     teacher = Enseignant.objects.get(user=request.user)
#     return render(request, 'accounts/teacher_dashboard.html', {
#         'teacher': teacher,
#     })



def user_logout(request):
     logout(request)
     messages.success(request, 'Vous avez été déconnecté avec succès.')
     return redirect('home')



def get_classes(request):
    departement_id = request.GET.get('departement_id')
    if departement_id:
        departement = get_object_or_404(Departement, id=departement_id)
        classes = Classe.objects.filter(departement=departement).values('id', 'nom_classe')
        return JsonResponse({'classes': list(classes)})
    else:
        return JsonResponse({'classes': []})