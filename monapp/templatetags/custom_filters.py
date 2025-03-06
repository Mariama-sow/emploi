from django import template
from django.template.defaultfilters import stringfilter
from datetime import datetime

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key, [])

@register.filter
def cours_heure(cours_list, heure):
    for cours in cours_list:
        # Vérifier si le cours commence à l'heure donnée
        if cours.heureDebut.hour == heure:
            # Calculer la durée du cours
            duree = cours.heureFin.hour - cours.heureDebut.hour
            return {
                'matiere': cours.matiere,
                'heureDebut': cours.heureDebut,
                'heureFin': cours.heureFin,
                'enseignant': cours.enseignant,
                'salle': cours.salle,
                'duree': duree,
            }
    return None

@register.filter
def subtract(value, arg):
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return 0
 
@register.filter(name='select_cours_heure')
def select_cours_heure(cours_list, heure):
    """
    Filtre personnalisé pour sélectionner un cours et gérer sa durée
    
    :param cours_list: Liste des cours pour un jour spécifique
    :param heure: Heure à filtrer
    :return: Cours pour l'heure spécifiée ou None
    """
    if not cours_list:
        return None
    
    # Convertir l'heure en entier si ce n'est pas déjà le cas
    heure = int(heure)
    
    for cours in cours_list:
        # Calculer la durée du cours en heures
        duree_cours = (cours['heure_fin'].hour - cours['heure_debut'].hour)
        
        # Vérifier si le cours commence à cette heure
        if cours['heure_debut'].hour == heure:
            # Ajouter l'information de fusion de lignes
            cours_avec_fusion = cours.copy()
            cours_avec_fusion['rowspan'] = duree_cours
            return cours_avec_fusion
        
        # Vérifier si l'heure fait partie de la durée du cours
        if (cours['heure_debut'].hour < heure < cours['heure_fin'].hour):
            # Retourner None pour les heures intermédiaires (déjà fusionnées)
            return 'skip'
    
    return None

@register.filter(name='get_rowspan')
def get_rowspan(cours_list, heure):
    """
    Filtre pour obtenir le rowspan d'un cours
    """
    if not cours_list:
        return 1
    
    heure = int(heure)
    
    for cours in cours_list:
        if cours['heure_debut'].hour == heure:
            return (cours['heure_fin'].hour - cours['heure_debut'].hour)
    
    return 1