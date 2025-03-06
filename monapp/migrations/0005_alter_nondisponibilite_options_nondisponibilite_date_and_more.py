# Generated by Django 5.1.6 on 2025-03-05 18:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('monapp', '0004_alter_elementdemodule_unique_together_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='nondisponibilite',
            options={'verbose_name_plural': 'Non-disponibilités'},
        ),
        migrations.AddField(
            model_name='nondisponibilite',
            name='date',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='nondisponibilite',
            name='heure_debut',
            field=models.TimeField(null=True),
        ),
        migrations.AddField(
            model_name='nondisponibilite',
            name='heure_fin',
            field=models.TimeField(null=True),
        ),
        migrations.AddField(
            model_name='nondisponibilite',
            name='raison',
            field=models.CharField(choices=[('personnel', 'Raison personnelle'), ('formation', 'Formation'), ('mission', 'Mission'), ('autre', 'Autre')], default='autre', max_length=20, null=True),
        ),
        migrations.AlterField(
            model_name='nondisponibilite',
            name='enseignant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='non_disponibilites', to='monapp.enseignant'),
        ),
        migrations.AlterUniqueTogether(
            name='nondisponibilite',
            unique_together={('enseignant', 'date', 'heure_debut', 'heure_fin')},
        ),
    ]
