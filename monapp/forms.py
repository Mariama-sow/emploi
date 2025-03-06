from django import forms
from .models import NonDisponibilite, ElementDeModule, Salle

class NonDisponibiliteForm(forms.ModelForm):
    class Meta:
        model = NonDisponibilite
        fields = [ 'jour', 'heure_debut', 'heure_fin', 'raison']
        widgets = {
            # 'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'jour': forms.Select(attrs={'class': 'form-control'}),
            'heure_debut': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'heure_fin': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'raison': forms.Select(attrs={'class': 'form-control'}),
        }
    
    # def clean(self):
    #     cleaned_data = super().clean()
    #     date = cleaned_data.get('date')
    #     jour = cleaned_data.get('jour')
        
    #     # Vérifier que le jour correspond à la date
    #     if date and jour:
    #         jour_semaine = date.strftime('%A').capitalize()
    #         if jour != jour_semaine:
    #             raise forms.ValidationError(f"Le jour sélectionné ({jour}) ne correspond pas au jour de la date ({jour_semaine})")
        
    #     return cleaned_data

class ElementDeModuleForm(forms.ModelForm):
    class Meta:
        model = ElementDeModule
        fields = ['matiere', 'volumeHoraire', 'jour', 'heureDebut', 'heureFin', 'salle']
        widgets = {
            'matiere': forms.TextInput(attrs={'class': 'form-control'}),
            'volumeHoraire': forms.NumberInput(attrs={'class': 'form-control'}),
            'jour': forms.Select(attrs={'class': 'form-control'}),
            'heureDebut': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'heureFin': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'salle': forms.Select(attrs={'class': 'form-control'}),
        }