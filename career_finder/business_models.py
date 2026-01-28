"""
Base de données des modèles de business rentables.
Chaque modèle est scoré selon différents critères pour le matching.
"""

BUSINESS_MODELS = {
    # === SERVICES / FREELANCE ===
    "freelance_dev": {
        "nom": "Développeur Freelance",
        "description": "Prestations de développement web/mobile pour des clients",
        "revenus_potentiels": "3 000 - 15 000€/mois",
        "temps_objectif_5k": "3-6 mois",
        "capital_requis": "0 - 500€",
        "scalabilite": 2,  # 1-5
        "competences_requises": ["Développement web/mobile"],
        "competences_bonus": ["Gestion de projet", "Vente/Négociation"],
        "modele_revenu": "Prestations de service (freelance, consulting)",
        "type_client": "B2B - Entreprises/Professionnels",
        "lieu": ["100% à domicile/remote", "Nomade digital - depuis n'importe où"],
        "visibilite": ["Modérément - je préfère rester en retrait", "Non - je veux un business anonyme/discret"],
        "risque": 1,
        "avantages": [
            "Démarrage rapide",
            "Faible investissement",
            "Forte demande",
            "Revenus élevés dès le début"
        ],
        "inconvenients": [
            "Échange temps contre argent",
            "Revenus non passifs",
            "Dépendance aux clients"
        ],
        "etapes_demarrage": [
            "Créer portfolio/GitHub",
            "S'inscrire sur Malt, Upwork, Comet",
            "Développer son réseau LinkedIn",
            "Définir ses tarifs (TJM 400-800€)"
        ],
        "ressources": ["Malt.fr", "Comet.co", "Upwork.com"]
    },

    "freelance_marketing": {
        "nom": "Consultant Marketing Digital",
        "description": "Accompagnement des entreprises en marketing digital, SEO, Ads",
        "revenus_potentiels": "3 000 - 12 000€/mois",
        "temps_objectif_5k": "4-8 mois",
        "capital_requis": "0 - 1 000€",
        "scalabilite": 3,
        "competences_requises": ["Marketing digital/SEO/Ads"],
        "competences_bonus": ["Rédaction/Copywriting", "Vente/Négociation"],
        "modele_revenu": "Prestations de service (freelance, consulting)",
        "type_client": "B2B - Entreprises/Professionnels",
        "lieu": ["100% à domicile/remote", "Nomade digital - depuis n'importe où"],
        "visibilite": ["Oui, je veux être le visage de mon business", "Oui, mais uniquement sur certains canaux"],
        "risque": 1,
        "avantages": [
            "Forte demande des PME",
            "Possibilité de revenus récurrents",
            "Peut évoluer vers une agence"
        ],
        "inconvenients": [
            "Concurrence forte",
            "Besoin de prouver ses résultats",
            "Clients parfois difficiles"
        ],
        "etapes_demarrage": [
            "Se certifier Google Ads/Meta",
            "Créer des études de cas",
            "Prospection LinkedIn",
            "Offrir un audit gratuit"
        ],
        "ressources": ["Google Skillshop", "HubSpot Academy", "Semrush Academy"]
    },

    "agence_digitale": {
        "nom": "Agence Digitale",
        "description": "Agence proposant des services web complets (dev, design, marketing)",
        "revenus_potentiels": "10 000 - 50 000€/mois",
        "temps_objectif_5k": "6-12 mois",
        "capital_requis": "2 000 - 10 000€",
        "scalabilite": 4,
        "competences_requises": ["Gestion de projet", "Vente/Négociation"],
        "competences_bonus": ["Développement web/mobile", "Marketing digital/SEO/Ads", "Design graphique/UI-UX"],
        "modele_revenu": "Prestations de service (freelance, consulting)",
        "type_client": "B2B - Entreprises/Professionnels",
        "lieu": ["100% à domicile/remote", "Local commercial/Bureau"],
        "visibilite": ["Oui, je veux être le visage de mon business"],
        "risque": 2,
        "avantages": [
            "Très scalable avec équipe",
            "Revenus récurrents possibles",
            "Valorisation pour revente"
        ],
        "inconvenients": [
            "Gestion d'équipe complexe",
            "Trésorerie à gérer",
            "Cycle de vente long"
        ],
        "etapes_demarrage": [
            "Définir son positionnement",
            "Constituer un réseau de freelances",
            "Créer site vitrine",
            "Prospection active"
        ],
        "ressources": ["Collective.work", "Notion templates agence"]
    },

    # === FORMATION / COACHING ===
    "formation_en_ligne": {
        "nom": "Formateur en Ligne",
        "description": "Création et vente de formations en ligne sur votre expertise",
        "revenus_potentiels": "2 000 - 30 000€/mois",
        "temps_objectif_5k": "6-12 mois",
        "capital_requis": "500 - 3 000€",
        "scalabilite": 5,
        "competences_requises": ["Pédagogie/Transmission"],
        "competences_bonus": ["Marketing digital/SEO/Ads", "Vidéo/Montage", "Rédaction/Copywriting"],
        "modele_revenu": "Vente de produits digitaux (formations, ebooks)",
        "type_client": "B2C - Particuliers",
        "lieu": ["100% à domicile/remote", "Nomade digital - depuis n'importe où"],
        "visibilite": ["Oui, je veux être le visage de mon business"],
        "risque": 2,
        "avantages": [
            "Revenus passifs",
            "Très scalable",
            "Travail depuis n'importe où",
            "Impact positif"
        ],
        "inconvenients": [
            "Long à construire l'audience",
            "Marché saturé",
            "Nécessite une expertise reconnue"
        ],
        "etapes_demarrage": [
            "Identifier son expertise monétisable",
            "Créer du contenu gratuit (YouTube, blog)",
            "Construire une liste email",
            "Créer une première formation"
        ],
        "ressources": ["Podia", "Teachable", "Systeme.io"]
    },

    "coaching": {
        "nom": "Coach/Consultant Expert",
        "description": "Accompagnement individuel ou groupe sur votre domaine d'expertise",
        "revenus_potentiels": "4 000 - 20 000€/mois",
        "temps_objectif_5k": "3-6 mois",
        "capital_requis": "0 - 1 000€",
        "scalabilite": 3,
        "competences_requises": ["Écoute et empathie", "Communication/Prise de parole"],
        "competences_bonus": ["Pédagogie/Transmission", "Marketing digital/SEO/Ads"],
        "modele_revenu": "Prestations de service (freelance, consulting)",
        "type_client": "Les deux me conviennent",
        "lieu": ["100% à domicile/remote", "Principalement à domicile avec déplacements occasionnels"],
        "visibilite": ["Oui, je veux être le visage de mon business"],
        "risque": 1,
        "avantages": [
            "Démarrage rapide",
            "Tarifs élevés possibles",
            "Relation client enrichissante"
        ],
        "inconvenients": [
            "Temps limité = revenus limités",
            "Besoin de crédibilité",
            "Énergie intensive"
        ],
        "etapes_demarrage": [
            "Définir sa spécialité/niche",
            "Créer une offre claire",
            "Témoignages clients",
            "Personal branding"
        ],
        "ressources": ["Calendly", "Zoom", "Notion"]
    },

    # === E-COMMERCE ===
    "ecommerce_marque": {
        "nom": "E-commerce Marque Propre",
        "description": "Création et vente de produits sous sa propre marque",
        "revenus_potentiels": "5 000 - 100 000€/mois",
        "temps_objectif_5k": "12-24 mois",
        "capital_requis": "5 000 - 30 000€",
        "scalabilite": 5,
        "competences_requises": ["Marketing digital/SEO/Ads"],
        "competences_bonus": ["Design graphique/UI-UX", "Gestion de projet"],
        "modele_revenu": "Vente de produits physiques",
        "type_client": "B2C - Particuliers",
        "lieu": ["100% à domicile/remote", "Local commercial/Bureau"],
        "visibilite": ["Non - je veux un business anonyme/discret", "Modérément - je préfère rester en retrait"],
        "risque": 3,
        "avantages": [
            "Asset revendable",
            "Très scalable",
            "Marges intéressantes"
        ],
        "inconvenients": [
            "Capital important",
            "Gestion stock/logistique",
            "Concurrence Amazon"
        ],
        "etapes_demarrage": [
            "Étude de marché",
            "Trouver fournisseur (Alibaba)",
            "Créer boutique Shopify",
            "Lancer Ads Facebook/Google"
        ],
        "ressources": ["Shopify", "Alibaba", "Oberlo"]
    },

    "amazon_fba": {
        "nom": "Amazon FBA",
        "description": "Vente de produits sur Amazon avec logistique gérée",
        "revenus_potentiels": "3 000 - 50 000€/mois",
        "temps_objectif_5k": "12-18 mois",
        "capital_requis": "5 000 - 20 000€",
        "scalabilite": 4,
        "competences_requises": [],
        "competences_bonus": ["Marketing digital/SEO/Ads", "Gestion de projet"],
        "modele_revenu": "Vente de produits physiques",
        "type_client": "B2C - Particuliers",
        "lieu": ["100% à domicile/remote"],
        "visibilite": ["Non - je veux un business anonyme/discret"],
        "risque": 3,
        "avantages": [
            "Logistique gérée par Amazon",
            "Accès à millions de clients",
            "Système éprouvé"
        ],
        "inconvenients": [
            "Dépendance à Amazon",
            "Marges réduites par les frais",
            "Concurrence féroce"
        ],
        "etapes_demarrage": [
            "Formation Amazon FBA",
            "Recherche produit avec Jungle Scout",
            "Négociation fournisseur",
            "Optimisation listing"
        ],
        "ressources": ["Jungle Scout", "Helium 10", "Amazon Seller Central"]
    },

    "dropshipping": {
        "nom": "Dropshipping",
        "description": "Vente en ligne sans stock, expédition directe fournisseur",
        "revenus_potentiels": "1 000 - 20 000€/mois",
        "temps_objectif_5k": "6-12 mois",
        "capital_requis": "500 - 3 000€",
        "scalabilite": 3,
        "competences_requises": ["Marketing digital/SEO/Ads"],
        "competences_bonus": ["Design graphique/UI-UX", "Rédaction/Copywriting"],
        "modele_revenu": "Vente de produits physiques",
        "type_client": "B2C - Particuliers",
        "lieu": ["100% à domicile/remote", "Nomade digital - depuis n'importe où"],
        "visibilite": ["Non - je veux un business anonyme/discret"],
        "risque": 2,
        "avantages": [
            "Peu de capital",
            "Pas de stock",
            "Test rapide de produits"
        ],
        "inconvenients": [
            "Marges faibles",
            "Qualité produit aléatoire",
            "SAV compliqué",
            "Modèle moins viable long terme"
        ],
        "etapes_demarrage": [
            "Choisir niche rentable",
            "Créer boutique Shopify",
            "Trouver produits gagnants",
            "Lancer publicités"
        ],
        "ressources": ["Shopify", "DSers", "CJ Dropshipping"]
    },

    # === SAAS / TECH ===
    "saas_micro": {
        "nom": "Micro-SaaS",
        "description": "Petit logiciel en ligne résolvant un problème spécifique",
        "revenus_potentiels": "2 000 - 30 000€/mois",
        "temps_objectif_5k": "12-24 mois",
        "capital_requis": "0 - 5 000€",
        "scalabilite": 5,
        "competences_requises": ["Développement web/mobile"],
        "competences_bonus": ["Marketing digital/SEO/Ads", "Design graphique/UI-UX"],
        "modele_revenu": "Abonnements/Revenus récurrents (SaaS, membership)",
        "type_client": "B2B - Entreprises/Professionnels",
        "lieu": ["100% à domicile/remote", "Nomade digital - depuis n'importe où"],
        "visibilite": ["Modérément - je préfère rester en retrait", "Non - je veux un business anonyme/discret"],
        "risque": 3,
        "avantages": [
            "Revenus récurrents",
            "Très scalable",
            "Asset très valorisé",
            "Automatisable"
        ],
        "inconvenients": [
            "Long à développer",
            "Besoin de compétences tech",
            "Support client"
        ],
        "etapes_demarrage": [
            "Identifier un problème récurrent",
            "Valider avec des prospects",
            "MVP rapide",
            "Itérer selon feedback"
        ],
        "ressources": ["Indie Hackers", "MicroConf", "SaaS Metrics"]
    },

    "saas_nocode": {
        "nom": "SaaS No-Code",
        "description": "Application SaaS créée avec des outils no-code",
        "revenus_potentiels": "1 000 - 15 000€/mois",
        "temps_objectif_5k": "12-18 mois",
        "capital_requis": "500 - 2 000€",
        "scalabilite": 4,
        "competences_requises": [],
        "competences_bonus": ["Marketing digital/SEO/Ads", "Design graphique/UI-UX", "Gestion de projet"],
        "modele_revenu": "Abonnements/Revenus récurrents (SaaS, membership)",
        "type_client": "Les deux me conviennent",
        "lieu": ["100% à domicile/remote", "Nomade digital - depuis n'importe où"],
        "visibilite": ["Modérément - je préfère rester en retrait"],
        "risque": 2,
        "avantages": [
            "Pas besoin de coder",
            "Lancement rapide",
            "Revenus récurrents"
        ],
        "inconvenients": [
            "Limitations techniques",
            "Coûts des outils",
            "Moins de contrôle"
        ],
        "etapes_demarrage": [
            "Apprendre Bubble/Webflow/Glide",
            "Identifier un problème niche",
            "Construire MVP",
            "Lancer et itérer"
        ],
        "ressources": ["Bubble.io", "Webflow", "Zapier", "Airtable"]
    },

    # === CONTENU / MÉDIA ===
    "youtube": {
        "nom": "YouTuber/Créateur de Contenu",
        "description": "Création de contenu vidéo monétisé",
        "revenus_potentiels": "1 000 - 50 000€/mois",
        "temps_objectif_5k": "18-36 mois",
        "capital_requis": "1 000 - 5 000€",
        "scalabilite": 4,
        "competences_requises": ["Vidéo/Montage", "Communication/Prise de parole"],
        "competences_bonus": ["Marketing digital/SEO/Ads", "Créativité/Innovation"],
        "modele_revenu": "Publicité/Contenu sponsorisé",
        "type_client": "B2C - Particuliers",
        "lieu": ["100% à domicile/remote", "Nomade digital - depuis n'importe où"],
        "visibilite": ["Oui, je veux être le visage de mon business"],
        "risque": 3,
        "avantages": [
            "Revenus passifs long terme",
            "Opportunités multiples",
            "Personal branding puissant"
        ],
        "inconvenients": [
            "Très long à construire",
            "Algorithme imprévisible",
            "Burnout créatif"
        ],
        "etapes_demarrage": [
            "Choisir sa niche",
            "Investir dans du bon matériel",
            "Publier régulièrement",
            "Optimiser SEO YouTube"
        ],
        "ressources": ["TubeBuddy", "VidIQ", "Canva"]
    },

    "newsletter_payante": {
        "nom": "Newsletter Payante",
        "description": "Newsletter premium avec contenu exclusif par abonnement",
        "revenus_potentiels": "1 000 - 20 000€/mois",
        "temps_objectif_5k": "12-24 mois",
        "capital_requis": "0 - 500€",
        "scalabilite": 4,
        "competences_requises": ["Rédaction/Copywriting"],
        "competences_bonus": ["Marketing digital/SEO/Ads", "Networking/Création de contacts"],
        "modele_revenu": "Abonnements/Revenus récurrents (SaaS, membership)",
        "type_client": "Les deux me conviennent",
        "lieu": ["100% à domicile/remote", "Nomade digital - depuis n'importe où"],
        "visibilite": ["Oui, je veux être le visage de mon business", "Oui, mais uniquement sur certains canaux"],
        "risque": 2,
        "avantages": [
            "Faible investissement",
            "Revenus récurrents",
            "Relation directe avec audience"
        ],
        "inconvenients": [
            "Long à construire l'audience",
            "Rythme de publication intense",
            "Taux de churn"
        ],
        "etapes_demarrage": [
            "Choisir sa thématique/angle",
            "Lancer version gratuite",
            "Construire audience",
            "Lancer offre payante"
        ],
        "ressources": ["Substack", "Beehiiv", "ConvertKit"]
    },

    "affiliation": {
        "nom": "Marketing d'Affiliation",
        "description": "Promotion de produits tiers contre commission",
        "revenus_potentiels": "1 000 - 30 000€/mois",
        "temps_objectif_5k": "12-24 mois",
        "capital_requis": "500 - 2 000€",
        "scalabilite": 4,
        "competences_requises": ["Marketing digital/SEO/Ads", "Rédaction/Copywriting"],
        "competences_bonus": [],
        "modele_revenu": "Affiliation/Commission",
        "type_client": "B2C - Particuliers",
        "lieu": ["100% à domicile/remote", "Nomade digital - depuis n'importe où"],
        "visibilite": ["Non - je veux un business anonyme/discret", "Modérément - je préfère rester en retrait"],
        "risque": 2,
        "avantages": [
            "Pas de produit à créer",
            "Revenus passifs",
            "Diversification possible"
        ],
        "inconvenients": [
            "Dépendance aux programmes",
            "SEO long à construire",
            "Commissions variables"
        ],
        "etapes_demarrage": [
            "Choisir niche rentable",
            "Créer site de contenu",
            "Stratégie SEO",
            "Rejoindre programmes affiliation"
        ],
        "ressources": ["Ahrefs", "Semrush", "Amazon Associates", "Awin"]
    },

    # === IMMOBILIER ===
    "immobilier_location": {
        "nom": "Investissement Locatif",
        "description": "Achat et mise en location de biens immobiliers",
        "revenus_potentiels": "500 - 5 000€/mois (par bien)",
        "temps_objectif_5k": "24-48 mois",
        "capital_requis": "20 000 - 100 000€ (apport)",
        "scalabilite": 4,
        "competences_requises": ["Immobilier"],
        "competences_bonus": ["Négociation", "Comptabilité/Finance"],
        "modele_revenu": "Abonnements/Revenus récurrents (SaaS, membership)",
        "type_client": "B2C - Particuliers",
        "lieu": ["Principalement à domicile avec déplacements occasionnels"],
        "visibilite": ["Non - je veux un business anonyme/discret"],
        "risque": 3,
        "avantages": [
            "Revenus passifs",
            "Valorisation du patrimoine",
            "Effet de levier bancaire"
        ],
        "inconvenients": [
            "Capital important",
            "Gestion locative",
            "Risques impayés"
        ],
        "etapes_demarrage": [
            "Formation immobilier",
            "Définir stratégie (LMNP, colocation, LCD)",
            "Recherche bien rentable",
            "Montage financier"
        ],
        "ressources": ["MeilleursAgents", "SeLoger", "Formations YouTube"]
    },

    "conciergerie_airbnb": {
        "nom": "Conciergerie Airbnb",
        "description": "Gestion de locations courte durée pour propriétaires",
        "revenus_potentiels": "2 000 - 15 000€/mois",
        "temps_objectif_5k": "6-12 mois",
        "capital_requis": "1 000 - 5 000€",
        "scalabilite": 3,
        "competences_requises": ["Organisation/Rigueur"],
        "competences_bonus": ["Négociation", "Networking/Création de contacts"],
        "modele_revenu": "Prestations de service (freelance, consulting)",
        "type_client": "B2B - Entreprises/Professionnels",
        "lieu": ["Sur le terrain/Chez les clients", "Principalement à domicile avec déplacements occasionnels"],
        "visibilite": ["Modérément - je préfère rester en retrait"],
        "risque": 2,
        "avantages": [
            "Marché en croissance",
            "Revenus récurrents",
            "Peu de capital"
        ],
        "inconvenients": [
            "Disponibilité 7j/7",
            "Gestion du personnel",
            "Saisonnalité"
        ],
        "etapes_demarrage": [
            "Étudier le marché local",
            "Créer offre de services",
            "Démarcher propriétaires",
            "Constituer équipe ménage"
        ],
        "ressources": ["PriceLabels", "Lodgify", "Guesty"]
    },

    # === SERVICES LOCAUX ===
    "services_entreprises": {
        "nom": "Services aux Entreprises (B2B local)",
        "description": "Services récurrents pour entreprises locales",
        "revenus_potentiels": "3 000 - 20 000€/mois",
        "temps_objectif_5k": "6-12 mois",
        "capital_requis": "1 000 - 10 000€",
        "scalabilite": 3,
        "competences_requises": ["Vente/Négociation"],
        "competences_bonus": ["Organisation/Rigueur", "Leadership/Management"],
        "modele_revenu": "Prestations de service (freelance, consulting)",
        "type_client": "B2B - Entreprises/Professionnels",
        "lieu": ["Sur le terrain/Chez les clients", "Local commercial/Bureau"],
        "visibilite": ["Modérément - je préfère rester en retrait"],
        "risque": 2,
        "avantages": [
            "Revenus récurrents",
            "Clients fidèles",
            "Scalable avec équipe"
        ],
        "inconvenients": [
            "Prospection terrain",
            "Gestion opérationnelle",
            "Ancrage local"
        ],
        "etapes_demarrage": [
            "Identifier service à forte demande",
            "Définir zone géographique",
            "Prospection directe",
            "Fidéliser par la qualité"
        ],
        "ressources": ["CRM HubSpot", "Calendly", "Linkedin Sales Navigator"]
    },

    # === AUTOMATISATION / IA ===
    "automatisation_ia": {
        "nom": "Services d'Automatisation/IA",
        "description": "Aide aux entreprises pour automatiser avec IA et no-code",
        "revenus_potentiels": "5 000 - 25 000€/mois",
        "temps_objectif_5k": "3-6 mois",
        "capital_requis": "0 - 1 000€",
        "scalabilite": 4,
        "competences_requises": [],
        "competences_bonus": ["Développement web/mobile", "Gestion de projet", "Résolution de problèmes"],
        "modele_revenu": "Prestations de service (freelance, consulting)",
        "type_client": "B2B - Entreprises/Professionnels",
        "lieu": ["100% à domicile/remote", "Nomade digital - depuis n'importe où"],
        "visibilite": ["Oui, mais uniquement sur certains canaux", "Modérément - je préfère rester en retrait"],
        "risque": 1,
        "tendances": ["Intelligence Artificielle", "Automatisation/No-code"],
        "avantages": [
            "Marché en explosion",
            "Tarifs élevés",
            "Forte demande",
            "Peut facturer au résultat"
        ],
        "inconvenients": [
            "Domaine en évolution rapide",
            "Besoin de se former continuellement",
            "Éducation du marché nécessaire"
        ],
        "etapes_demarrage": [
            "Se former sur Make/Zapier/n8n + ChatGPT API",
            "Créer études de cas",
            "Cibler PME qui ont des process manuels",
            "Proposer audit gratuit"
        ],
        "ressources": ["Make.com", "Zapier", "n8n", "OpenAI API"]
    },

    "agence_ia": {
        "nom": "Agence IA/Chatbots",
        "description": "Création de solutions IA personnalisées pour entreprises",
        "revenus_potentiels": "8 000 - 50 000€/mois",
        "temps_objectif_5k": "4-8 mois",
        "capital_requis": "1 000 - 5 000€",
        "scalabilite": 4,
        "competences_requises": ["Développement web/mobile"],
        "competences_bonus": ["Vente/Négociation", "Gestion de projet"],
        "modele_revenu": "Prestations de service (freelance, consulting)",
        "type_client": "B2B - Entreprises/Professionnels",
        "lieu": ["100% à domicile/remote"],
        "visibilite": ["Oui, je veux être le visage de mon business"],
        "risque": 2,
        "tendances": ["Intelligence Artificielle"],
        "avantages": [
            "Marché naissant",
            "Tarifs très élevés",
            "Positionnement expert"
        ],
        "inconvenients": [
            "Compétences techniques requises",
            "Cycle de vente long",
            "Technologie évolutive"
        ],
        "etapes_demarrage": [
            "Maîtriser les APIs LLM",
            "Créer des démos impressionnantes",
            "Se positionner sur LinkedIn",
            "Cibler secteurs à fort potentiel"
        ],
        "ressources": ["OpenAI", "Anthropic", "Langchain", "Voiceflow"]
    }
}

# Catégories pour le filtrage
CATEGORIES = {
    "services": ["freelance_dev", "freelance_marketing", "agence_digitale", "coaching", "services_entreprises", "automatisation_ia", "agence_ia"],
    "formation": ["formation_en_ligne", "coaching"],
    "ecommerce": ["ecommerce_marque", "amazon_fba", "dropshipping"],
    "tech": ["saas_micro", "saas_nocode", "agence_ia"],
    "contenu": ["youtube", "newsletter_payante", "affiliation"],
    "immobilier": ["immobilier_location", "conciergerie_airbnb"],
    "ia_tendance": ["automatisation_ia", "agence_ia", "saas_micro"]
}
