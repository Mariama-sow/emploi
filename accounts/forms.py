from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model
from monapp.models import Etudiant, Enseignant, Classe, Departement

User = get_user_model()

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Nom d'utilisateur", widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput(attrs={'class': 'form-control'}))





class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label="Confirmer le mot de passe", widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    
    # Champs conditionnels selon le rôle
    matricule = forms.CharField(
        required=False,
        max_length=12,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text="Format requis: 12 caractères maximum"
    )
    specialite = forms.CharField(
        required=False,
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    departement = forms.ModelChoiceField(
        queryset=Departement.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_departement'})
    )
    classe = forms.ModelChoiceField(
        queryset=Classe.objects.none(),  # Initialement vide, sera rempli via JavaScript
        required=False,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_classe'})
    )
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si un département est déjà sélectionné, filtrez les classes en conséquence
        if 'departement' in self.data:
            try:
                departement_id = int(self.data.get('departement'))
                self.fields['classe'].queryset = Classe.objects.filter(departement_id=departement_id)
            except (ValueError, TypeError):
                pass  # Ignorer les erreurs de conversion

    class Meta:
        model = User
        fields = ['last_name', 'first_name', 'username', 'email', 'role']
        widgets = {
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_password2(self):
        if self.cleaned_data.get('password') != self.cleaned_data.get('password2'):
            raise forms.ValidationError("Les mots de passe ne correspondent pas.")
        return self.cleaned_data['password2']

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        matricule = cleaned_data.get('matricule')
        classe = cleaned_data.get('classe')
        specialite = cleaned_data.get('specialite')
        departement = cleaned_data.get('departement')

        print("Rôle:", role)
        print("Matricule:", matricule)
        print("Classe:", classe)
        print("Spécialité:", specialite)
        print("Département:", departement)

        if role == 'etudiant':
            if not matricule:
                raise forms.ValidationError("Le matricule est obligatoire pour les étudiants.")
            if not departement:
                raise forms.ValidationError("Le département est obligatoire pour les étudiants.")
            if not classe:
                raise forms.ValidationError("La classe est obligatoire pour les étudiants.")
            # Vérifier si le matricule existe déjà
            if Etudiant.objects.filter(matricule=matricule).exists():
                raise forms.ValidationError("Ce matricule existe déjà.")
        
        elif role == 'enseignant':
            if not specialite:
                raise forms.ValidationError("La spécialité est obligatoire pour les enseignants.")

        return cleaned_data