from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    tel = models.CharField(max_length=20, blank=True, null=True)
    role = models.CharField(max_length=50, choices=[
        ('admin', 'Administrateur'),
        ('enseignant', 'Enseignant'),
        ('etudiant', 'Étudiant')
    ], default='etudiant')

    def __str__(self):
        return f"{self.username} - {self.role}"
