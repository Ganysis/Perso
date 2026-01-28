#!/usr/bin/env python3
"""
Script de démonstration 2026 - Simule un profil et affiche l'analyse.
Pour tester le vrai questionnaire interactif: python3 main.py

Inclut les nouveaux critères: réseau, expérience, localisation, etc.
"""

from career_finder.analyzer import generate_report, analyze_profile

# Profil de test simulé - VERSION 2026
profil_test = {
    # Situation actuelle
    "statut_actuel": "En poste salarié",
    "revenus_actuels": "2 500 - 4 000€",
    "epargne_disponible": "5 000 - 15 000€",
    "temps_disponible": "10-20h (mi-temps)",
    "urgence": "Modérée - objectif dans 1-2 ans",

    # NOUVEAU: Contexte personnel
    "localisation": "Grande ville (Lyon, Marseille, Bordeaux, etc.)",
    "situation_familiale": "En couple sans enfant",
    "seul_revenu": "Non, mon/ma conjoint(e) a des revenus stables",
    "contraintes_perso": ["Aucune contrainte particulière"],

    # NOUVEAU: Expérience entrepreneuriale
    "deja_entrepris": "Oui, un side project (non rentable)",
    "echec_passe": ["Manque de temps"],
    "vente_experience": "Oui, des prestations freelance",

    # NOUVEAU: Réseau & Assets
    "reseau_linkedin": "300 - 500",
    "clients_potentiels": "Oui, 3-5 contacts chauds",
    "audience_existante": "Petite (moins de 500 followers/abonnés)",
    "assets_existants": ["Portfolio/Site web personnel"],

    # Compétences
    "competences_tech": ["Développement web/mobile", "Marketing digital/SEO/Ads"],
    "competences_soft": ["Vente/Négociation", "Gestion de projet", "Résolution de problèmes"],
    "expertise_secteur": "Tech/Software/SaaS",
    "apprentissage": "Oui, je suis motivé pour apprendre pendant 6-12 mois",

    # Préférences business
    "modele_revenu": "Abonnements/Revenus récurrents (SaaS, membership)",
    "type_client": "B2B - Entreprises/Professionnels",
    "scalabilite": "Importante - je veux pouvoir déléguer à terme",
    "risque": "Modéré - ok pour investir si ROI probable",
    "visibilite": "Modérément - je préfère rester en retrait",

    # Style de vie
    "lieu_travail": "100% à domicile/remote",
    "horaires": "Flexibles - je gère comme je veux",
    "solo_equipe": "Seul - je suis autonome",
    "impact": "Important - mais pas au détriment de la rentabilité",

    # Intérêts - TENDANCES 2026
    "passions": ["Tech/Innovation/IA", "Finance/Investissement"],
    "secteurs_exclus": "",
    "tendances": ["IA Générative / Agents IA", "Automatisation business (Make, n8n, Zapier)"],

    # Objectifs financiers
    "objectif_1_delai": "12 mois",
    "objectif_2_delai": "24 mois",
    "reinvestissement": "50-70% réinvesti",
    "exit_strategy": "Peut-être, si bonne opportunité"
}

print("=" * 60)
print("🧪 DÉMONSTRATION - Analyse d'un profil test")
print("=" * 60)
print()
print("📋 Profil simulé:")
print(f"   • Statut: {profil_test['statut_actuel']}")
print(f"   • Capital: {profil_test['epargne_disponible']}")
print(f"   • Temps dispo: {profil_test['temps_disponible']}")
print(f"   • Compétences: {', '.join(profil_test['competences_tech'])}")
print(f"   • Modèle préféré: {profil_test['modele_revenu']}")
print()
print("=" * 60)
print()

# Générer et afficher le rapport
rapport = generate_report(profil_test, top_n=5)
print(rapport)

print()
print("=" * 60)
print("💡 Pour faire le VRAI questionnaire interactif:")
print("   python3 main.py")
print("=" * 60)
