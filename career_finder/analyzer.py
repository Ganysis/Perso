"""
Analyseur de profil entrepreneurial.
Match les réponses utilisateur avec les business models les plus adaptés.
"""

from .business_models import BUSINESS_MODELS


def calculate_match_score(reponses: dict, business: dict) -> dict:
    """
    Calcule un score de matching entre le profil utilisateur et un business model.
    Retourne un dict avec le score et les raisons.
    """
    score = 0
    max_score = 0
    raisons_positives = []
    raisons_negatives = []

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
        "Tech/Innovation/IA": ["saas_micro", "saas_nocode", "automatisation_ia", "agence_ia", "freelance_dev"],
        "Finance/Investissement": ["immobilier_location", "coaching"],
        "Santé/Fitness/Bien-être": ["coaching", "formation_en_ligne"],
        "E-commerce/Retail": ["ecommerce_marque", "amazon_fba", "dropshipping"],
        "Éducation/Formation": ["formation_en_ligne", "coaching", "youtube"],
        "Développement personnel": ["coaching", "formation_en_ligne"]
    }
    for passion in passions:
        if passion in keywords_passion:
            business_id = list(BUSINESS_MODELS.keys())[list(BUSINESS_MODELS.values()).index(business)]
            if business_id in keywords_passion[passion]:
                score += 5
                raisons_positives.append(f"Match avec votre passion: {passion}")
                break

    # === 10. DÉLAI OBJECTIF 5K ===
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

    # Calcul du pourcentage
    pourcentage = round((score / max_score) * 100) if max_score > 0 else 0

    return {
        "score": score,
        "max_score": max_score,
        "pourcentage": pourcentage,
        "raisons_positives": raisons_positives,
        "raisons_negatives": raisons_negatives
    }


def get_business_id(business: dict) -> str:
    """Retrouve l'ID d'un business model."""
    for bid, bdata in BUSINESS_MODELS.items():
        if bdata == business:
            return bid
    return "unknown"


def analyze_profile(reponses: dict) -> list:
    """
    Analyse le profil complet et retourne les business models classés par pertinence.
    """
    resultats = []

    for business_id, business in BUSINESS_MODELS.items():
        match_data = calculate_match_score(reponses, business)
        resultats.append({
            "id": business_id,
            "business": business,
            **match_data
        })

    # Trier par score décroissant
    resultats.sort(key=lambda x: x["pourcentage"], reverse=True)

    return resultats


def generate_report(reponses: dict, top_n: int = 5) -> str:
    """
    Génère un rapport complet avec les recommandations.
    """
    resultats = analyze_profile(reponses)
    top_resultats = resultats[:top_n]

    report = []
    report.append("=" * 60)
    report.append("🎯 RAPPORT - PROJETS ENTREPRENEURIAUX RECOMMANDÉS")
    report.append("=" * 60)
    report.append("")
    report.append("📊 Objectifs rappelés:")
    report.append("   • Objectif 1: 5 000€ net/mois")
    report.append("   • Objectif 2: 8 000€ net/mois (5k + 3k assistant)")
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
    report.append("")
    report.append("📌 Autres options à considérer:")
    for resultat in resultats[top_n:top_n+3]:
        business = resultat["business"]
        report.append(f"   • {business['nom']} ({resultat['pourcentage']}%)")

    report.append("")
    report.append("=" * 60)
    report.append("💡 Prochaines étapes recommandées:")
    report.append("   1. Approfondir le top 1-2 projets")
    report.append("   2. Faire une étude de marché rapide")
    report.append("   3. Définir un MVP ou première offre")
    report.append("   4. Fixer des objectifs à 30/60/90 jours")
    report.append("=" * 60)

    return "\n".join(report)
