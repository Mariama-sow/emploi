from django.db import models
from django.forms import ValidationError
from accounts.models import CustomUser



class Enseignant(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    specialite = models.CharField(max_length=100)

    def get_matieres(self):
        """Retourne les matières enseignées par cet enseignant"""
        return self.elementdemodule_set.values_list('matiere', flat=True).distinct()

    def __str__(self):
        return f"{self.user.username} - {self.specialite}"
class NonDisponibilite(models.Model):
    JOURS_CHOICES = [
        ('Lundi', 'Lundi'),
        ('Mardi', 'Mardi'),
        ('Mercredi', 'Mercredi'),
        ('Jeudi', 'Jeudi'),
        ('Vendredi', 'Vendredi'),
        ('Samedi', 'Samedi'),
        ('Dimanche', 'Dimanche'),
    ]
    
    RAISON_CHOICES = [
        ('personnel', 'Raison personnelle'),
        ('formation', 'Formation'),
        ('mission', 'Mission'),
        ('autre', 'Autre'),
    ]
    
    enseignant = models.ForeignKey(Enseignant, on_delete=models.CASCADE, related_name='non_disponibilites')
    date = models.DateField(null=True, blank=True)
    jour = models.CharField(max_length=10, choices=JOURS_CHOICES)
    heure_debut = models.TimeField(null=True)
    heure_fin = models.TimeField(null=True)
    raison = models.CharField(max_length=20, choices=RAISON_CHOICES, default='autre', null=True)
    
    def clean(self):
        # Validation : heure de fin doit être après heure de début
        if self.heure_debut and self.heure_fin and self.heure_debut >= self.heure_fin:
            raise ValidationError("L'heure de fin doit être après l'heure de début.")

        # Vérifier si self.enseignant_id est défini avant de l'utiliser
        if self.enseignant_id:  
            chevauchements = NonDisponibilite.objects.filter(
                enseignant_id=self.enseignant_id,  # ✅ Utilisation de `enseignant_id`
                date=self.date,
                heure_debut__lt=self.heure_fin,
                heure_fin__gt=self.heure_debut
            ).exclude(pk=self.pk)

            if chevauchements.exists():
                raise ValidationError("Cette non-disponibilité chevauche une autre non-disponibilité existante.")
    
    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.enseignant} - {self.jour} {self.date} ({self.heure_debut}-{self.heure_fin})"
    
    class Meta:
        verbose_name_plural = "Non-disponibilités"
        unique_together = ['enseignant', 'date', 'heure_debut', 'heure_fin']
    

class Salle(models.Model):
    numSalle = models.CharField(max_length=10, unique=True)
    capacite = models.IntegerField()
    typeSalle = models.CharField(max_length=50)

    def __str__(self):
       return self.numSalle  # Pour le modèle Departement


class ElementDeModule(models.Model):
    JOURS_CHOICES = [
        ('Lundi', 'Lundi'), ('Mardi', 'Mardi'), ('Mercredi', 'Mercredi'),
        ('Jeudi', 'Jeudi'), ('Vendredi', 'Vendredi'), 
        ('Samedi', 'Samedi'), ('Dimanche', 'Dimanche'),
    ]

    matiere = models.CharField(max_length=100)
    volumeHoraire = models.IntegerField(help_text="Volume horaire par session de cours")
    volumeHoraireSemestre = models.IntegerField(help_text="Volume horaire total pour le semestre",null=True)
    heureDebut = models.TimeField()
    jour = models.CharField(max_length=10, choices=JOURS_CHOICES)
    heureFin = models.TimeField()
    
    enseignant = models.ForeignKey(Enseignant, on_delete=models.CASCADE)
    salle = models.ForeignKey('Salle', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Lien avec les classes
    classes = models.ManyToManyField('Classe', through='CoursClasse')

    def clean(self):
        # Vérification des horaires
        if self.heureFin <= self.heureDebut:
            raise ValidationError("L'heure de fin doit être après l'heure de début.")

        # Vérification des conflits pour l'enseignant
        conflits_enseignant = ElementDeModule.objects.filter(
            enseignant=self.enseignant,
            jour=self.jour
        ).exclude(id=self.id).filter(
            heureDebut__lt=self.heureFin,
            heureFin__gt=self.heureDebut
        )

        if conflits_enseignant.exists():
            raise ValidationError("Conflit d'horaires pour cet enseignant.")

        # Vérification des conflits de salle
        if self.salle:
            conflits_salle = ElementDeModule.objects.filter(
                salle=self.salle,
                jour=self.jour
            ).exclude(id=self.id).filter(
                heureDebut__lt=self.heureFin,
                heureFin__gt=self.heureDebut
            )

            if conflits_salle.exists():
                raise ValidationError("Conflit de salle.")

        # Validation du volume horaire
        if self.volumeHoraire > self.volumeHoraireSemestre:
            raise ValidationError("Le volume horaire par session ne peut pas dépasser le volume horaire total du semestre.")

    def calculer_nombre_sessions(self):
        """Calcule le nombre de sessions nécessaires pour couvrir le volume horaire du semestre"""
        return self.volumeHoraireSemestre // self.volumeHoraire

    def __str__(self):
        return f"{self.matiere} - {self.enseignant}"
    

# Département, Filière et Classe
class Departement(models.Model):
    nom_departement = models.CharField(max_length=100)
    nombreSem = models.IntegerField()
    chefdepartement = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return self.nom_departement



class Classe(models.Model):
    nom_classe = models.CharField(max_length=100)
    nbrEleves = models.IntegerField()
    departement = models.ForeignKey('Departement', on_delete=models.CASCADE)
    
    def get_emploi_du_temps(self):
        """Retourne l'emploi du temps de la classe"""
        return ElementDeModule.objects.filter(classes=self).order_by('jour', 'heureDebut')

    def __str__(self):
        return self.nom_classe
    
class Etudiant(models.Model):
    matricule = models.CharField(max_length=12, unique=True)
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    classe = models.ForeignKey(Classe, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.matricule} - {self.user.username}"

# Semestre
class Semestre(models.Model):
    dateDebut = models.DateField()
    dateFin = models.DateField()
    num = models.IntegerField()
    anneeUniv = models.CharField(max_length=10)
   
    def __str__(self):
        return f"Salle {self.num}"
    

class CoursClasse(models.Model):
    cours = models.ForeignKey(ElementDeModule, on_delete=models.CASCADE)
    classe = models.ForeignKey('Classe', on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('cours', 'classe')
        verbose_name = "Association Cours-Classe"
        verbose_name_plural = "Associations Cours-Classes"

    def __str__(self):
        return f"{self.cours.matiere} - {self.classe.nom_classe}"