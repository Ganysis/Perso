"""
Analyseur de profil entrepreneurial.
Match les réponses utilisateur avec les business models les plus adaptés.

Version 2026 - Filtres éliminatoires + scoring avancé.
"""

from .business_models import BUSINESS_MODELS


# =============================================================================
# FILTRES ÉLIMINATOIRES (DEALBREAKERS)
# Si une condition est remplie, le business est EXCLU
# =============================================================================

DEALBREAKERS = {
    # === URGENCE FINANCIÈRE ===
    # Si urgence très forte (3-6 mois), exclure les business longs
    "urgence_tres_forte": {
        "condition_field": "urgence",
        "condition_value": "Très forte - besoin de revenus sous 3-6 mois",
        "exclude_businesses": [
            "saas_micro", "saas_nocode", "formation_en_ligne", "blogging_seo",
            "newsletter_sponsorisee", "ecommerce_marque", "immobilier_lcd",
            "immobilier_colocation", "vente_etsy", "template_themes",
            "produits_alimentaires"
        ],
        "reason": "❌ Trop long pour votre urgence (3-6 mois)"
    },
    "urgence_forte": {
        "condition_field": "urgence",
        "condition_value": "Forte - besoin de résultats sous 6-12 mois",
        "exclude_businesses": [
            "saas_micro", "formation_en_ligne", "blogging_seo",
            "newsletter_sponsorisee", "immobilier_lcd", "immobilier_colocation"
        ],
        "reason": "❌ Délai incompatible avec votre urgence (6-12 mois)"
    },

    # === CAPITAL ===
    # Si capital 0€, exclure les business qui nécessitent investissement
    "capital_zero": {
        "condition_field": "epargne_disponible",
        "condition_value": "0€ (bootstrap total)",
        "exclude_businesses": [
            "ecommerce_marque", "immobilier_lcd", "immobilier_colocation",
            "produits_alimentaires", "traiteur", "nettoyage_entreprises",
            "jardinage_paysagiste", "lavage_auto", "photographe",
            "freelance_video", "renovation_bricolage"
        ],
        "reason": "❌ Capital insuffisant (0€ disponible)"
    },
    "capital_faible": {
        "condition_field": "epargne_disponible",
        "condition_value": "1 - 1 000€",
        "exclude_businesses": [
            "ecommerce_marque", "immobilier_lcd", "immobilier_colocation",
            "produits_alimentaires", "agence_recrutement"
        ],
        "reason": "❌ Capital insuffisant (< 1 000€)"
    },

    # === TEMPS DISPONIBLE ===
    # Si moins de 5h/semaine, exclure les business chronophages
    "temps_minimal": {
        "condition_field": "temps_disponible",
        "condition_value": "Moins de 5h (side project léger)",
        "exclude_businesses": [
            "nettoyage_entreprises", "services_seniors", "renovation_bricolage",
            "jardinage_paysagiste", "lavage_auto", "traiteur", "conciergerie_airbnb",
            "wedding_planner", "event_entreprise", "photographe",
            "agence_seo", "agence_ads", "agence_web", "agence_recrutement"
        ],
        "reason": "❌ Requiert plus de 5h/semaine"
    },
    "temps_faible": {
        "condition_field": "temps_disponible",
        "condition_value": "5-10h (side project sérieux)",
        "exclude_businesses": [
            "nettoyage_entreprises", "services_seniors", "traiteur",
            "conciergerie_airbnb", "wedding_planner", "event_entreprise"
        ],
        "reason": "❌ Requiert plus de 10h/semaine"
    },

    # === LOCALISATION ===
    # Si zone rurale, exclure certains services locaux
    "localisation_rurale": {
        "condition_field": "localisation",
        "condition_value": "Zone rurale / Village",
        "exclude_businesses": [
            "conciergerie_airbnb", "lavage_auto", "nettoyage_entreprises",
            "event_entreprise", "agence_recrutement"
        ],
        "reason": "❌ Marché insuffisant en zone rurale"
    },

    # === RÉSEAU ===
    # Si aucun réseau, exclure les business qui dépendent du réseau
    "reseau_zero": {
        "condition_field": "reseau_linkedin",
        "condition_value": "Moins de 100",
        "exclude_if_also": {
            "field": "clients_potentiels",
            "value": "Non, aucun"
        },
        "exclude_businesses": [
            "coaching_business", "agence_recrutement", "consulting_direction",
            "podcast_b2b"
        ],
        "reason": "❌ Réseau insuffisant pour ce business"
    },

    # === EXPÉRIENCE VENTE ===
    # Si jamais vendu, pénaliser fortement certains business
    "jamais_vendu": {
        "condition_field": "vente_experience",
        "condition_value": "Non, jamais",
        "exclude_businesses": [
            "agence_recrutement", "coaching_business", "event_entreprise"
        ],
        "reason": "⚠️ Expérience vente requise"
    },

    # === CONTRAINTES PERSONNELLES ===
    "mobilite_reduite": {
        "condition_field": "contraintes_perso",
        "condition_values": ["Mobilité réduite ou handicap"],
        "exclude_businesses": [
            "renovation_bricolage", "jardinage_paysagiste", "nettoyage_entreprises",
            "lavage_auto", "traiteur", "photographe", "wedding_planner"
        ],
        "reason": "❌ Incompatible avec mobilité réduite"
    }
}


def check_dealbreakers(reponses: dict, business_id: str) -> tuple[bool, str]:
    """
    Vérifie si un business est exclu par les dealbreakers.
    Retourne (is_excluded, reason).
    """
    for rule_name, rule in DEALBREAKERS.items():
        # Vérifier la condition principale
        field = rule.get("condition_field")
        user_value = reponses.get(field, "")

        # Pour les champs multi-choix
        if "condition_values" in rule:
            # Vérifie si une des valeurs est dans la réponse utilisateur
            if isinstance(user_value, list):
                match = any(v in user_value for v in rule["condition_values"])
            else:
                match = user_value in rule["condition_values"]
        else:
            match = user_value == rule.get("condition_value")

        if not match:
            continue

        # Vérifier condition additionnelle si présente
        if "exclude_if_also" in rule:
            also_field = rule["exclude_if_also"]["field"]
            also_value = rule["exclude_if_also"]["value"]
            if reponses.get(also_field) != also_value:
                continue

        # Vérifier si ce business est dans la liste d'exclusion
        if business_id in rule.get("exclude_businesses", []):
            return True, rule.get("reason", "Incompatible avec votre profil")

    return False, ""


def calculate_match_score(reponses: dict, business: dict, business_id: str = None) -> dict:
    """
    Calcule un score de matching entre le profil utilisateur et un business model.
    Retourne un dict avec le score et les raisons.

    Version 2026 - Scoring avancé avec nouveaux critères.
    """
    score = 0
    max_score = 0
    raisons_positives = []
    raisons_negatives = []
    warnings = []

    # === VÉRIFICATION DEALBREAKERS D'ABORD ===
    if business_id:
        is_excluded, exclusion_reason = check_dealbreakers(reponses, business_id)
        if is_excluded:
            return {
                "score": 0,
                "max_score": 100,
                "pourcentage": 0,
                "raisons_positives": [],
                "raisons_negatives": [exclusion_reason],
                "excluded": True,
                "exclusion_reason": exclusion_reason
            }

    # === 1. COMPÉTENCES (poids: 25) ===
    max_score += 25
    competences_user = set(reponses.get("competences_tech", []) + reponses.get("competences_soft", []))
    competences_requises = set(business.get("competences_requises", []))
    competences_bonus = set(business.get("competences_bonus", []))

    # Compétences requises
    if competences_requises:
        match_requises = competences_user & competences_requises
        if len(match_requises) == len(competences_requises):
            score += 20
            raisons_positives.append(f"Vous avez toutes les compétences requises")
        elif len(match_requises) > 0:
            score += 10
            manquantes = competences_requises - competences_user
            raisons_negatives.append(f"Compétences à acquérir: {', '.join(manquantes)}")
        else:
            raisons_negatives.append(f"Compétences requises manquantes: {', '.join(competences_requises)}")
    else:
        score += 15  # Pas de compétences requises = accessible
        raisons_positives.append("Aucune compétence spécifique requise")

    # Compétences bonus
    match_bonus = competences_user & competences_bonus
    if match_bonus:
        score += 5
        raisons_positives.append(f"Compétences bonus: {', '.join(match_bonus)}")

    # === 2. CAPITAL DISPONIBLE (poids: 20) ===
    max_score += 20
    capital_mapping = {
        "0€ (bootstrap total)": 0,
        "1 - 1 000€": 500,
        "1 000 - 5 000€": 3000,
        "5 000 - 15 000€": 10000,
        "15 000 - 50 000€": 30000,
        "Plus de 50 000€": 75000
    }
    capital_user = capital_mapping.get(reponses.get("epargne_disponible", ""), 0)

    capital_requis_str = business.get("capital_requis", "0€")
    # Parse le capital requis (prend la valeur max)
    try:
        capital_requis = int(''.join(filter(str.isdigit, capital_requis_str.split("-")[-1].split("€")[0])))
    except:
        capital_requis = 0

    if capital_user >= capital_requis:
        score += 20
        raisons_positives.append(f"Capital suffisant ({business['capital_requis']})")
    elif capital_user >= capital_requis * 0.5:
        score += 10
        raisons_negatives.append(f"Capital limite - idéal: {business['capital_requis']}")
    else:
        raisons_negatives.append(f"Capital insuffisant - requis: {business['capital_requis']}")

    # === 3. MODÈLE DE REVENU (poids: 15) ===
    max_score += 15
    modele_user = reponses.get("modele_revenu", "")
    if modele_user == business.get("modele_revenu") or modele_user == "Peu importe, tant que c'est rentable":
        score += 15
        raisons_positives.append(f"Modèle de revenu aligné")
    elif modele_user:
        score += 5

    # === 4. TYPE DE CLIENT (poids: 10) ===
    max_score += 10
    client_user = reponses.get("type_client", "")
    client_business = business.get("type_client", "")
    if client_user == client_business or client_user == "Les deux me conviennent" or client_business == "Les deux me conviennent":
        score += 10
    elif client_user:
        score += 3

    # === 5. LIEU DE TRAVAIL (poids: 10) ===
    max_score += 10
    lieu_user = reponses.get("lieu_travail", "")
    lieux_business = business.get("lieu", [])
    if lieu_user in lieux_business or lieu_user == "Peu importe":
        score += 10
        raisons_positives.append("Compatible avec votre lieu de travail souhaité")
    elif lieux_business:
        score += 3

    # === 6. VISIBILITÉ (poids: 10) ===
    max_score += 10
    visibilite_user = reponses.get("visibilite", "")
    visibilites_business = business.get("visibilite", [])
    if visibilite_user in visibilites_business:
        score += 10
    else:
        score += 5

    # === 7. SCALABILITÉ vs PRÉFÉRENCE (poids: 10) ===
    max_score += 10
    scalabilite_pref = reponses.get("scalabilite", "")
    scalabilite_business = business.get("scalabilite", 3)

    if "Essentielle" in scalabilite_pref and scalabilite_business >= 4:
        score += 10
        raisons_positives.append("Excellente scalabilité")
    elif "Importante" in scalabilite_pref and scalabilite_business >= 3:
        score += 8
    elif "solo" in scalabilite_pref and scalabilite_business <= 2:
        score += 10
    else:
        score += 5

    # === 8. TENDANCES (bonus: +10) ===
    tendances_user = set(reponses.get("tendances", []))
    tendances_business = set(business.get("tendances", []))
    if tendances_user & tendances_business:
        score += 10
        max_score += 10
        raisons_positives.append(f"Aligné avec tendances: {', '.join(tendances_user & tendances_business)}")

    # === 9. PASSIONS / INTÉRÊTS (bonus) ===
    passions = set(reponses.get("passions", []))
    keywords_passion = {
        "Tech/Innovation/IA": ["saas_micro", "saas_nocode", "automatisation_ia", "freelance_dev", "agent_ia_builder", "prompt_engineer"],
        "Finance/Investissement": ["immobilier_lcd", "immobilier_colocation", "coaching_business"],
        "Santé/Fitness/Bien-être": ["coaching_carriere", "coaching_business", "formation_en_ligne"],
        "E-commerce/Retail": ["ecommerce_marque", "vente_etsy", "revente_occasions"],
        "Éducation/Formation": ["formation_en_ligne", "coaching_business", "mentor_tech"],
        "Développement personnel": ["coaching_carriere", "coaching_business", "formation_en_ligne"],
        "Food/Restauration": ["traiteur", "produits_alimentaires"],
        "Immobilier": ["immobilier_lcd", "immobilier_colocation", "conciergerie_airbnb"],
        "Art/Créativité": ["freelance_design", "freelance_video", "photographe", "vente_etsy"]
    }
    if business_id:
        for passion in passions:
            if passion in keywords_passion and business_id in keywords_passion[passion]:
                score += 5
                raisons_positives.append(f"Match avec votre passion: {passion}")
                break

    # === 10. RÉSEAU & CLIENTS POTENTIELS (poids: 15) ===
    max_score += 15
    reseau_mapping = {
        "Moins de 100": 1,
        "100 - 300": 2,
        "300 - 500": 3,
        "500 - 1000": 4,
        "Plus de 1000": 5
    }
    clients_mapping = {
        "Non, aucun": 0,
        "Peut-être 1-2 personnes": 1,
        "Oui, 3-5 contacts chauds": 3,
        "Oui, 5-10 contacts potentiels": 4,
        "Oui, plus de 10 contacts qualifiés": 5
    }
    reseau_score = reseau_mapping.get(reponses.get("reseau_linkedin", ""), 1)
    clients_score = clients_mapping.get(reponses.get("clients_potentiels", ""), 0)

    # Business qui nécessitent du réseau
    business_needs_network = ["coaching_business", "agence_recrutement", "event_entreprise",
                              "podcast_b2b", "freelance_marketing", "agence_seo", "agence_ads"]

    if business_id in business_needs_network:
        if reseau_score >= 3 and clients_score >= 3:
            score += 15
            raisons_positives.append("Réseau solide pour ce business")
        elif reseau_score >= 2 or clients_score >= 1:
            score += 8
            raisons_negatives.append("Réseau à développer pour optimiser")
        else:
            score += 3
            raisons_negatives.append("⚠️ Réseau faible - difficile de démarrer")
    else:
        # Business qui ne nécessitent pas de réseau
        score += 10
        if clients_score >= 3:
            score += 5
            raisons_positives.append("Clients potentiels identifiés")

    # === 11. EXPÉRIENCE ENTREPRENEURIALE (poids: 10) ===
    max_score += 10
    exp_mapping = {
        "Non, c'est ma première fois": 0,
        "Oui, un side project (non rentable)": 1,
        "Oui, un projet qui a généré des revenus": 3,
        "Oui, plusieurs projets": 4,
        "Oui, j'ai déjà eu une entreprise rentable": 5
    }
    vente_mapping = {
        "Non, jamais": 0,
        "Oui, sur Leboncoin/Vinted (particulier)": 1,
        "Oui, des prestations freelance": 3,
        "Oui, j'ai un rôle commercial dans mon job": 4,
        "Oui, je vends régulièrement (entrepreneur)": 5
    }
    exp_score = exp_mapping.get(reponses.get("deja_entrepris", ""), 0)
    vente_score = vente_mapping.get(reponses.get("vente_experience", ""), 0)

    # Business qui demandent de l'expérience
    business_needs_experience = ["agence_seo", "agence_ads", "agence_recrutement",
                                  "coaching_business", "event_entreprise"]

    if business_id in business_needs_experience:
        if exp_score >= 3 or vente_score >= 3:
            score += 10
            raisons_positives.append("Expérience entrepreneuriale valorisée")
        elif exp_score >= 1 or vente_score >= 1:
            score += 5
        else:
            raisons_negatives.append("⚠️ Peu d'expérience - courbe d'apprentissage")
    else:
        score += 7
        if exp_score >= 3:
            score += 3
            raisons_positives.append("Expérience passée = avantage")

    # === 12. DÉLAI OBJECTIF 5K ===
    max_score += 10
    delai_user = reponses.get("objectif_1_delai", "12 mois")
    delai_business = business.get("temps_objectif_5k", "12 mois")

    delai_mapping = {"6 mois": 6, "12 mois": 12, "18 mois": 18, "24 mois": 24, "Plus de 24 mois": 36}
    try:
        mois_user = delai_mapping.get(delai_user, 12)
        mois_business = int(delai_business.split("-")[0])
    except:
        mois_user = 12
        mois_business = 12

    if mois_business <= mois_user:
        score += 10
        raisons_positives.append(f"Objectif 5k€ atteignable: {delai_business}")
    elif mois_business <= mois_user + 6:
        score += 5
        raisons_negatives.append(f"Délai optimiste - réaliste: {delai_business}")
    else:
        raisons_negatives.append(f"Délai plus long que souhaité: {delai_business}")

    # === 13. SCORE DE RÉALISME DU BUSINESS ===
    realisme = business.get("realisme", 3)
    if realisme >= 5:
        score += 5
        raisons_positives.append("✓ Business très réaliste (5/5)")
    elif realisme >= 4:
        score += 3
    elif realisme <= 2:
        raisons_negatives.append("⚠️ Business risqué / difficile")

    # Calcul du pourcentage
    pourcentage = round((score / max_score) * 100) if max_score > 0 else 0

    return {
        "score": score,
        "max_score": max_score,
        "pourcentage": pourcentage,
        "raisons_positives": raisons_positives,
        "raisons_negatives": raisons_negatives,
        "excluded": False
    }


def get_business_id(business: dict) -> str:
    """Retrouve l'ID d'un business model."""
    for bid, bdata in BUSINESS_MODELS.items():
        if bdata == business:
            return bid
    return "unknown"


def analyze_profile(reponses: dict) -> tuple[list, list]:
    """
    Analyse le profil complet et retourne:
    - Les business models classés par pertinence
    - Les business exclus avec leurs raisons

    Version 2026 - Avec filtres éliminatoires.
    """
    resultats = []
    exclus = []

    for business_id, business in BUSINESS_MODELS.items():
        match_data = calculate_match_score(reponses, business, business_id)

        result_item = {
            "id": business_id,
            "business": business,
            **match_data
        }

        if match_data.get("excluded", False):
            exclus.append(result_item)
        else:
            resultats.append(result_item)

    # Trier par score décroissant
    resultats.sort(key=lambda x: x["pourcentage"], reverse=True)
    exclus.sort(key=lambda x: x["business"]["nom"])

    return resultats, exclus


def generate_report(reponses: dict, top_n: int = 5) -> str:
    """
    Génère un rapport complet avec les recommandations.

    Version 2026 - Inclut les exclusions et warnings.
    """
    resultats, exclus = analyze_profile(reponses)
    top_resultats = resultats[:top_n]

    report = []
    report.append("=" * 60)
    report.append("🎯 RAPPORT 2026 - PROJETS ENTREPRENEURIAUX RECOMMANDÉS")
    report.append("=" * 60)
    report.append("")
    report.append("📊 Objectifs rappelés:")
    report.append("   • Objectif 1: 5 000€ net/mois")
    report.append("   • Objectif 2: 8 000€ net/mois (5k + 3k assistant)")
    report.append("")

    # Afficher le nombre de business analysés vs exclus
    report.append(f"📈 Analyse: {len(resultats)} business compatibles / {len(exclus)} exclus")
    report.append("")
    report.append("-" * 60)

    for i, resultat in enumerate(top_resultats, 1):
        business = resultat["business"]
        report.append("")
        report.append(f"🏆 #{i} - {business['nom']} ({resultat['pourcentage']}% de compatibilité)")
        report.append("-" * 40)
        report.append(f"📝 {business['description']}")
        report.append(f"💰 Revenus potentiels: {business['revenus_potentiels']}")
        report.append(f"⏱️  Temps pour 5k€: {business['temps_objectif_5k']}")
        report.append(f"💵 Capital requis: {business['capital_requis']}")
        report.append(f"📈 Scalabilité: {'⭐' * business['scalabilite']}{'☆' * (5 - business['scalabilite'])}")

        if resultat["raisons_positives"]:
            report.append("")
            report.append("✅ Points forts pour vous:")
            for raison in resultat["raisons_positives"]:
                report.append(f"   • {raison}")

        if resultat["raisons_negatives"]:
            report.append("")
            report.append("⚠️  Points d'attention:")
            for raison in resultat["raisons_negatives"]:
                report.append(f"   • {raison}")

        report.append("")
        report.append("📋 Étapes pour démarrer:")
        for j, etape in enumerate(business.get("etapes_demarrage", []), 1):
            report.append(f"   {j}. {etape}")

        report.append("")
        report.append("🔗 Ressources:")
        for ressource in business.get("ressources", []):
            report.append(f"   • {ressource}")

        report.append("")
        report.append("=" * 60)

    # Résumé des business moins compatibles mais intéressants
    if len(resultats) > top_n:
        report.append("")
        report.append("📌 Autres options à considérer:")
        for resultat in resultats[top_n:top_n+3]:
            business = resultat["business"]
            report.append(f"   • {business['nom']} ({resultat['pourcentage']}%)")

    # === SECTION EXCLUSIONS ===
    if exclus:
        report.append("")
        report.append("=" * 60)
        report.append("🚫 BUSINESS EXCLUS (incompatibles avec votre profil)")
        report.append("-" * 60)
        for ex in exclus[:10]:  # Limiter à 10 pour lisibilité
            business = ex["business"]
            reason = ex.get("exclusion_reason", "Incompatible")
            report.append(f"   • {business['nom']}: {reason}")
        if len(exclus) > 10:
            report.append(f"   ... et {len(exclus) - 10} autres")

    report.append("")
    report.append("=" * 60)
    report.append("💡 Prochaines étapes recommandées:")
    report.append("   1. Approfondir le top 1-2 projets")
    report.append("   2. Faire une étude de marché rapide")
    report.append("   3. Définir un MVP ou première offre")
    report.append("   4. Fixer des objectifs à 30/60/90 jours")
    report.append("=" * 60)

    return "\n".join(report)
