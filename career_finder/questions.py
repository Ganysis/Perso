"""
Questions pour identifier le meilleur projet entrepreneurial.
Orienté création d'entreprise rentable avec objectifs :
- Objectif 1 : 5 000€ net/mois
- Objectif 2 : 8 000€ net/mois (5k + 3k assistant)

Mise à jour 2026 - Questions approfondies pour recommandations précises.
"""

QUESTIONS = {
    "situation_actuelle": {
        "titre": "📍 Situation Actuelle",
        "questions": [
            {
                "id": "statut_pro",
                "question": "Quel est votre statut professionnel actuel ?",
                "type": "choix",
                "options": [
                    "Salarié CDI",
                    "Salarié CDD",
                    "Freelance/Indépendant",
                    "Sans emploi",
                    "Étudiant",
                    "En reconversion"
                ]
            },
            {
                "id": "revenus_actuels",
                "question": "Quels sont vos revenus mensuels nets actuels ?",
                "type": "choix",
                "options": [
                    "0 - 1 500€",
                    "1 500 - 2 500€",
                    "2 500 - 4 000€",
                    "4 000 - 6 000€",
                    "Plus de 6 000€"
                ]
            },
            {
                "id": "epargne_disponible",
                "question": "Quel capital pouvez-vous investir dans votre projet ?",
                "type": "choix",
                "options": [
                    "0€ (bootstrap total)",
                    "1 - 1 000€",
                    "1 000 - 5 000€",
                    "5 000 - 15 000€",
                    "15 000 - 50 000€",
                    "Plus de 50 000€"
                ]
            },
            {
                "id": "temps_disponible",
                "question": "Combien de temps pouvez-vous consacrer à votre projet par semaine ?",
                "type": "choix",
                "options": [
                    "Moins de 5h (side project léger)",
                    "5-10h (side project sérieux)",
                    "10-20h (mi-temps)",
                    "20-35h (quasi temps plein)",
                    "35h+ (temps plein dédié)"
                ]
            },
            {
                "id": "urgence",
                "question": "Quelle est votre urgence financière ?",
                "type": "choix",
                "options": [
                    "Aucune - je peux attendre 2-3 ans",
                    "Modérée - objectif dans 1-2 ans",
                    "Forte - besoin de résultats sous 6-12 mois",
                    "Très forte - besoin de revenus sous 3-6 mois"
                ]
            }
        ]
    },

    "contexte_personnel": {
        "titre": "👤 Contexte Personnel (CRITIQUE)",
        "questions": [
            {
                "id": "localisation",
                "question": "Où êtes-vous situé ?",
                "type": "choix",
                "options": [
                    "Paris / Île-de-France",
                    "Grande ville (Lyon, Marseille, Bordeaux, etc.)",
                    "Ville moyenne (50k-200k habitants)",
                    "Petite ville (10k-50k habitants)",
                    "Zone rurale / Village",
                    "Étranger (francophone)",
                    "Étranger (non francophone)"
                ]
            },
            {
                "id": "situation_familiale",
                "question": "Quelle est votre situation familiale ?",
                "type": "choix",
                "options": [
                    "Seul(e) sans enfant",
                    "En couple sans enfant",
                    "Seul(e) avec enfant(s)",
                    "En couple avec enfant(s)",
                    "Autre situation"
                ]
            },
            {
                "id": "seul_revenu",
                "question": "Êtes-vous le seul revenu du foyer ?",
                "type": "choix",
                "options": [
                    "Oui, je suis le seul revenu",
                    "Non, mon/ma conjoint(e) a des revenus stables",
                    "Non, nous avons d'autres sources (rentes, aides, etc.)",
                    "Non applicable (je vis seul)"
                ]
            },
            {
                "id": "contraintes_perso",
                "question": "Avez-vous des contraintes personnelles à prendre en compte ?",
                "type": "multi_choix",
                "options": [
                    "Horaires fixes (enfants, école, etc.)",
                    "Mobilité réduite ou handicap",
                    "Obligations familiales (parents, etc.)",
                    "Visa/Permis de travail limité",
                    "Santé fragile / fatigue chronique",
                    "Aucune contrainte particulière"
                ]
            }
        ]
    },

    "experience_entrepreneuriale": {
        "titre": "🚀 Expérience Entrepreneuriale",
        "questions": [
            {
                "id": "deja_entrepris",
                "question": "Avez-vous déjà lancé un projet entrepreneurial ?",
                "type": "choix",
                "options": [
                    "Non, c'est ma première fois",
                    "Oui, un side project (non rentable)",
                    "Oui, un projet qui a généré des revenus",
                    "Oui, plusieurs projets",
                    "Oui, j'ai déjà eu une entreprise rentable"
                ]
            },
            {
                "id": "echec_passe",
                "question": "Si vous avez déjà entrepris, qu'est-ce qui n'a pas marché ?",
                "type": "multi_choix",
                "options": [
                    "Pas d'expérience passée",
                    "Manque de temps",
                    "Manque d'argent",
                    "Mauvais produit/marché",
                    "Problèmes de vente/marketing",
                    "Problèmes techniques",
                    "Problèmes personnels/motivation",
                    "Associé/équipe",
                    "Mon projet a fonctionné"
                ]
            },
            {
                "id": "vente_experience",
                "question": "Avez-vous déjà vendu quelque chose (produit, service, à n'importe qui) ?",
                "type": "choix",
                "options": [
                    "Non, jamais",
                    "Oui, sur Leboncoin/Vinted (particulier)",
                    "Oui, des prestations freelance",
                    "Oui, j'ai un rôle commercial dans mon job",
                    "Oui, je vends régulièrement (entrepreneur)"
                ]
            }
        ]
    },

    "reseau_assets": {
        "titre": "🔗 Réseau & Assets Existants",
        "questions": [
            {
                "id": "reseau_linkedin",
                "question": "Combien de contacts professionnels avez-vous (LinkedIn ou équivalent) ?",
                "type": "choix",
                "options": [
                    "Moins de 100",
                    "100 - 300",
                    "300 - 500",
                    "500 - 1000",
                    "Plus de 1000"
                ]
            },
            {
                "id": "clients_potentiels",
                "question": "Avez-vous des contacts qui pourraient devenir clients ?",
                "type": "choix",
                "options": [
                    "Non, aucun",
                    "Peut-être 1-2 personnes",
                    "Oui, 3-5 contacts chauds",
                    "Oui, 5-10 contacts potentiels",
                    "Oui, plus de 10 contacts qualifiés"
                ]
            },
            {
                "id": "audience_existante",
                "question": "Avez-vous une audience existante (email, réseaux sociaux) ?",
                "type": "choix",
                "options": [
                    "Non, aucune",
                    "Petite (moins de 500 followers/abonnés)",
                    "Moyenne (500 - 2000)",
                    "Grande (2000 - 10000)",
                    "Très grande (plus de 10000)"
                ]
            },
            {
                "id": "assets_existants",
                "question": "Avez-vous des assets existants réutilisables ?",
                "type": "multi_choix",
                "options": [
                    "Portfolio/Site web personnel",
                    "Blog avec du trafic",
                    "Chaîne YouTube/Podcast",
                    "Newsletter avec abonnés",
                    "Communauté (Discord, groupe FB, etc.)",
                    "Code/Produit technique existant",
                    "Base de données/contacts qualifiés",
                    "Aucun asset particulier"
                ]
            }
        ]
    },

    "competences": {
        "titre": "💪 Compétences & Savoir-faire",
        "questions": [
            {
                "id": "competences_tech",
                "question": "Quelles compétences techniques possédez-vous ? (plusieurs choix possibles)",
                "type": "multi_choix",
                "options": [
                    "Développement web/mobile",
                    "Design graphique/UI-UX",
                    "Marketing digital/SEO/Ads",
                    "Rédaction/Copywriting",
                    "Vidéo/Montage",
                    "Comptabilité/Finance",
                    "Vente/Négociation",
                    "Gestion de projet",
                    "Artisanat/Manuel",
                    "Cuisine/Restauration",
                    "Santé/Bien-être",
                    "Juridique",
                    "Immobilier",
                    "Aucune compétence technique particulière"
                ]
            },
            {
                "id": "competences_soft",
                "question": "Quelles sont vos forces relationnelles ? (plusieurs choix possibles)",
                "type": "multi_choix",
                "options": [
                    "Communication/Prise de parole",
                    "Écoute et empathie",
                    "Leadership/Management",
                    "Négociation",
                    "Networking/Création de contacts",
                    "Pédagogie/Transmission",
                    "Créativité/Innovation",
                    "Organisation/Rigueur",
                    "Résolution de problèmes",
                    "Patience/Persévérance"
                ]
            },
            {
                "id": "expertise_domaine",
                "question": "Dans quel(s) domaine(s) avez-vous une expertise ou expérience significative ?",
                "type": "texte",
                "placeholder": "Ex: 10 ans en logistique, expertise en nutrition sportive, etc."
            },
            {
                "id": "apprentissage",
                "question": "Êtes-vous prêt à apprendre de nouvelles compétences ?",
                "type": "choix",
                "options": [
                    "Oui, je suis motivé pour apprendre pendant 6-12 mois",
                    "Oui, mais formation courte (1-3 mois max)",
                    "Préfère utiliser mes compétences actuelles",
                    "Dépend du ROI de la formation"
                ]
            }
        ]
    },

    "preferences_business": {
        "titre": "🎯 Préférences Business",
        "questions": [
            {
                "id": "modele_revenu",
                "question": "Quel modèle de revenus vous attire le plus ?",
                "type": "choix",
                "options": [
                    "Prestations de service (freelance, consulting)",
                    "Vente de produits physiques",
                    "Vente de produits digitaux (formations, ebooks)",
                    "Abonnements/Revenus récurrents (SaaS, membership)",
                    "Affiliation/Commission",
                    "Publicité/Contenu sponsorisé",
                    "Peu importe, tant que c'est rentable"
                ]
            },
            {
                "id": "type_client",
                "question": "Avec quel type de clients préférez-vous travailler ?",
                "type": "choix",
                "options": [
                    "B2B - Entreprises/Professionnels",
                    "B2C - Particuliers",
                    "Les deux me conviennent",
                    "Pas de contact client direct (produits automatisés)"
                ]
            },
            {
                "id": "scalabilite",
                "question": "Quelle importance accordez-vous à la scalabilité ?",
                "type": "choix",
                "options": [
                    "Essentielle - je veux un business qui scale sans moi",
                    "Importante - je veux pouvoir déléguer à terme",
                    "Modérée - je peux échanger mon temps contre de l'argent au début",
                    "Peu importante - je veux rester solo"
                ]
            },
            {
                "id": "risque",
                "question": "Quel niveau de risque êtes-vous prêt à prendre ?",
                "type": "choix",
                "options": [
                    "Minimal - je veux des revenus prévisibles",
                    "Modéré - ok pour investir si ROI probable",
                    "Élevé - prêt à tout miser sur un projet prometteur"
                ]
            },
            {
                "id": "visibilite",
                "question": "Êtes-vous à l'aise avec la visibilité publique ?",
                "type": "choix",
                "options": [
                    "Oui, je veux être le visage de mon business",
                    "Oui, mais uniquement sur certains canaux",
                    "Modérément - je préfère rester en retrait",
                    "Non - je veux un business anonyme/discret"
                ]
            }
        ]
    },

    "style_vie": {
        "titre": "🌴 Style de Vie Souhaité",
        "questions": [
            {
                "id": "lieu_travail",
                "question": "Où souhaitez-vous travailler ?",
                "type": "choix",
                "options": [
                    "100% à domicile/remote",
                    "Principalement à domicile avec déplacements occasionnels",
                    "Local commercial/Bureau",
                    "Sur le terrain/Chez les clients",
                    "Nomade digital - depuis n'importe où",
                    "Peu importe"
                ]
            },
            {
                "id": "horaires",
                "question": "Quels horaires de travail souhaitez-vous ?",
                "type": "choix",
                "options": [
                    "Horaires classiques (9h-18h)",
                    "Flexibles - je gère comme je veux",
                    "Intensifs au début puis automatisation",
                    "Temps partiel avec revenus passifs"
                ]
            },
            {
                "id": "solo_equipe",
                "question": "Préférez-vous travailler seul ou en équipe ?",
                "type": "choix",
                "options": [
                    "Seul - je suis autonome",
                    "Avec un associé",
                    "Avec une petite équipe (2-5 personnes)",
                    "Peu importe, selon les besoins du business"
                ]
            },
            {
                "id": "impact",
                "question": "L'impact social/environnemental est-il important pour vous ?",
                "type": "choix",
                "options": [
                    "Essentiel - je veux un business à impact positif",
                    "Important - mais pas au détriment de la rentabilité",
                    "Secondaire - focus sur la rentabilité d'abord",
                    "Non pertinent pour moi"
                ]
            }
        ]
    },

    "interets_secteurs": {
        "titre": "🔥 Intérêts & Secteurs",
        "questions": [
            {
                "id": "passions",
                "question": "Quels sont vos centres d'intérêt et passions ?",
                "type": "multi_choix",
                "options": [
                    "Tech/Innovation/IA",
                    "Finance/Investissement",
                    "Santé/Fitness/Bien-être",
                    "Mode/Beauté",
                    "Food/Restauration",
                    "Voyage/Tourisme",
                    "Immobilier",
                    "E-commerce/Retail",
                    "Éducation/Formation",
                    "Divertissement/Gaming",
                    "Art/Créativité",
                    "Sport",
                    "Développement personnel",
                    "Écologie/Durabilité",
                    "Automobile",
                    "Animaux"
                ]
            },
            {
                "id": "secteurs_exclus",
                "question": "Y a-t-il des secteurs que vous excluez ?",
                "type": "texte",
                "placeholder": "Ex: alcool, tabac, paris en ligne, etc."
            },
            {
                "id": "tendances",
                "question": "Quelles tendances 2026 vous semblent prometteuses ?",
                "type": "multi_choix",
                "options": [
                    "IA Générative / Agents IA",
                    "Automatisation business (Make, n8n, Zapier)",
                    "Prompt Engineering / IA appliquée",
                    "Remote work / Travail asynchrone",
                    "Santé mentale / Bien-être",
                    "Silver économie (seniors)",
                    "Seconde main / Économie circulaire",
                    "Cybersécurité / Protection données",
                    "Formation professionnelle / Upskilling",
                    "Services B2B externalisés",
                    "Énergie / Rénovation énergétique",
                    "Mobilité douce / Vélo"
                ]
            }
        ]
    },

    "objectifs_financiers": {
        "titre": "💰 Objectifs Financiers",
        "questions": [
            {
                "id": "objectif_1_delai",
                "question": "En combien de temps voulez-vous atteindre 5 000€ net/mois ?",
                "type": "choix",
                "options": [
                    "6 mois",
                    "12 mois",
                    "18 mois",
                    "24 mois",
                    "Plus de 24 mois"
                ]
            },
            {
                "id": "objectif_2_delai",
                "question": "En combien de temps voulez-vous atteindre 8 000€ net/mois (avec assistant) ?",
                "type": "choix",
                "options": [
                    "12 mois",
                    "18 mois",
                    "24 mois",
                    "36 mois",
                    "Plus de 36 mois"
                ]
            },
            {
                "id": "reinvestissement",
                "question": "Quelle part des bénéfices êtes-vous prêt à réinvestir ?",
                "type": "choix",
                "options": [
                    "Tout réinvestir jusqu'à l'objectif",
                    "50-70% réinvesti",
                    "30-50% réinvesti",
                    "Minimum - je veux maximiser mes revenus immédiats"
                ]
            },
            {
                "id": "exit_strategy",
                "question": "Envisagez-vous de revendre votre business un jour ?",
                "type": "choix",
                "options": [
                    "Oui, c'est l'objectif principal",
                    "Peut-être, si bonne opportunité",
                    "Non, je veux des revenus long terme",
                    "Je n'y ai pas encore réfléchi"
                ]
            }
        ]
    }
}
