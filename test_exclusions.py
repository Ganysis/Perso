#!/usr/bin/env python3
"""
Test des filtres d'exclusion - Profil avec contraintes fortes.
"""

from career_finder.analyzer import generate_report, analyze_profile

# Profil CONTRAINT - urgence forte, peu de capital, peu de temps
profil_contraint = {
    # Situation actuelle - CONTRAINTE
    "statut_actuel": "Sans emploi",
    "revenus_actuels": "0 - 1 500€",
    "epargne_disponible": "0€ (bootstrap total)",  # PAS DE CAPITAL
    "temps_disponible": "Moins de 5h (side project léger)",  # PEU DE TEMPS
    "urgence": "Très forte - besoin de revenus sous 3-6 mois",  # URGENCE FORTE

    # Contexte personnel
    "localisation": "Zone rurale / Village",  # RURAL
    "situation_familiale": "Seul(e) avec enfant(s)",
    "seul_revenu": "Oui, je suis le seul revenu",
    "contraintes_perso": ["Horaires fixes (enfants, école, etc.)"],

    # Expérience
    "deja_entrepris": "Non, c'est ma première fois",
    "echec_passe": ["Pas d'expérience passée"],
    "vente_experience": "Non, jamais",

    # Réseau
    "reseau_linkedin": "Moins de 100",
    "clients_potentiels": "Non, aucun",
    "audience_existante": "Non, aucune",
    "assets_existants": ["Aucun asset particulier"],

    # Compétences
    "competences_tech": ["Rédaction/Copywriting"],
    "competences_soft": ["Organisation/Rigueur"],
    "apprentissage": "Oui, mais formation courte (1-3 mois max)",

    # Préférences
    "modele_revenu": "Prestations de service (freelance, consulting)",
    "type_client": "B2C - Particuliers",
    "scalabilite": "Peu importante - je veux rester solo",
    "risque": "Minimal - je veux des revenus prévisibles",
    "visibilite": "Non - je veux un business anonyme/discret",

    # Style de vie
    "lieu_travail": "100% à domicile/remote",
    "horaires": "Horaires classiques (9h-18h)",
    "solo_equipe": "Seul - je suis autonome",
    "impact": "Non pertinent pour moi",

    # Intérêts
    "passions": ["Développement personnel"],
    "secteurs_exclus": "",
    "tendances": ["Formation professionnelle / Upskilling"],

    # Objectifs
    "objectif_1_delai": "6 mois",
    "objectif_2_delai": "12 mois",
    "reinvestissement": "Minimum - je veux maximiser mes revenus immédiats",
    "exit_strategy": "Non, je veux des revenus long terme"
}

print("=" * 60)
print("🧪 TEST EXCLUSIONS - Profil très contraint")
print("=" * 60)
print()
print("📋 Profil simulé:")
print(f"   • Capital: {profil_contraint['epargne_disponible']}")
print(f"   • Temps: {profil_contraint['temps_disponible']}")
print(f"   • Urgence: {profil_contraint['urgence']}")
print(f"   • Localisation: {profil_contraint['localisation']}")
print(f"   • Réseau: {profil_contraint['reseau_linkedin']}")
print(f"   • Expérience vente: {profil_contraint['vente_experience']}")
print()
print("=" * 60)
print()

# Générer et afficher le rapport
rapport = generate_report(profil_contraint, top_n=5)
print(rapport)
