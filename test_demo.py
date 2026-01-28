#!/usr/bin/env python3
"""
Script de démonstration - Simule un profil et affiche l'analyse.
Pour tester le vrai questionnaire interactif: python3 main.py
"""

from career_finder.analyzer import generate_report, analyze_profile

# Profil de test simulé
profil_test = {
    # Situation actuelle
    "statut_actuel": "En poste salarié",
    "revenus_actuels": "2 000 - 3 000€ net/mois",
    "epargne_disponible": "5 000 - 15 000€",
    "temps_disponible": "10-20 heures/semaine (side project)",
    "urgence_financiere": "Confortable - je veux augmenter mes revenus sans pression",

    # Compétences
    "competences_tech": ["Développement web/mobile", "Marketing digital/SEO/Ads"],
    "competences_soft": ["Vente/Négociation", "Gestion de projet"],
    "expertise_secteur": "Tech/Software/SaaS",
    "apprentissage": "Oui, motivé pour apprendre",

    # Préférences business
    "modele_revenu": "Abonnements/Revenus récurrents (SaaS, membership)",
    "type_client": "B2B - Entreprises/Professionnels",
    "scalabilite": "Importante - je veux pouvoir grandir",
    "tolerance_risque": "Modéré - je préfère un équilibre risque/sécurité",
    "visibilite": "Modérément - je préfère rester en retrait",

    # Style de vie
    "lieu_travail": "100% à domicile/remote",
    "heures_travail": "Flexibles - résultats plutôt que présence",
    "solo_equipe": "Solo au début, équipe si ça décolle",
    "impact": "Fort - je veux contribuer à quelque chose de plus grand",

    # Intérêts
    "passions": ["Tech/Innovation/IA", "Finance/Investissement"],
    "secteurs_exclus": ["Crypto/NFT/Trading"],
    "tendances": ["Intelligence Artificielle", "Automatisation/No-code"],

    # Objectifs financiers
    "objectif_1_delai": "12 mois",
    "objectif_2_delai": "24 mois",
    "reinvestissement": "50% - équilibre croissance et revenus",
    "exit_strategy": "Peut-être un jour, si belle opportunité"
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
