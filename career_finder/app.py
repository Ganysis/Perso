"""
Application principale - Interface interactive pour trouver son projet entrepreneurial.
Objectifs: 5 000€ net/mois puis 8 000€ net/mois (avec assistant)
"""

import json
import os
from datetime import datetime
from .questions import QUESTIONS
from .analyzer import analyze_profile, generate_report


class CareerFinder:
    def __init__(self):
        self.reponses = {}
        self.data_dir = os.path.join(os.path.dirname(__file__), "data")
        os.makedirs(self.data_dir, exist_ok=True)

    def clear_screen(self):
        """Efface l'écran du terminal."""
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_header(self):
        """Affiche l'en-tête de l'application."""
        print("\n" + "=" * 60)
        print("🚀 CAREER PROJECT FINDER - Trouvez votre projet rentable")
        print("=" * 60)
        print("💰 Objectif 1: 5 000€ net/mois")
        print("💰 Objectif 2: 8 000€ net/mois (+ 3k assistant)")
        print("=" * 60 + "\n")

    def print_section_header(self, titre: str):
        """Affiche l'en-tête d'une section."""
        print("\n" + "-" * 50)
        print(f"{titre}")
        print("-" * 50 + "\n")

    def ask_choice_question(self, question: dict) -> str:
        """Pose une question à choix unique."""
        print(f"❓ {question['question']}\n")
        options = question["options"]

        for i, option in enumerate(options, 1):
            print(f"   {i}. {option}")

        while True:
            try:
                print()
                choix = input("👉 Votre choix (numéro): ").strip()
                if choix.lower() == 'q':
                    return None
                index = int(choix) - 1
                if 0 <= index < len(options):
                    print(f"   ✓ {options[index]}\n")
                    return options[index]
                else:
                    print("   ⚠️  Numéro invalide, réessayez.")
            except ValueError:
                print("   ⚠️  Entrez un numéro valide.")

    def ask_multi_choice_question(self, question: dict) -> list:
        """Pose une question à choix multiples."""
        print(f"❓ {question['question']}")
        print("   (Entrez les numéros séparés par des virgules, ex: 1,3,5)\n")
        options = question["options"]

        for i, option in enumerate(options, 1):
            print(f"   {i}. {option}")

        while True:
            try:
                print()
                choix = input("👉 Vos choix (numéros): ").strip()
                if choix.lower() == 'q':
                    return None
                if not choix:
                    print("   ⚠️  Sélectionnez au moins une option.")
                    continue

                indices = [int(x.strip()) - 1 for x in choix.split(",")]
                selections = []
                valid = True

                for index in indices:
                    if 0 <= index < len(options):
                        selections.append(options[index])
                    else:
                        print(f"   ⚠️  Numéro {index + 1} invalide.")
                        valid = False
                        break

                if valid and selections:
                    print("   ✓ Sélectionné:")
                    for s in selections:
                        print(f"     • {s}")
                    print()
                    return selections

            except ValueError:
                print("   ⚠️  Format invalide. Utilisez: 1,2,3")

    def ask_text_question(self, question: dict) -> str:
        """Pose une question à réponse libre."""
        print(f"❓ {question['question']}")
        if "placeholder" in question:
            print(f"   💡 Exemple: {question['placeholder']}")
        print()

        reponse = input("👉 Votre réponse: ").strip()
        if reponse.lower() == 'q':
            return None
        if not reponse:
            reponse = "(non renseigné)"
        print(f"   ✓ {reponse}\n")
        return reponse

    def ask_question(self, question: dict):
        """Pose une question selon son type."""
        q_type = question.get("type", "choix")

        if q_type == "choix":
            return self.ask_choice_question(question)
        elif q_type == "multi_choix":
            return self.ask_multi_choice_question(question)
        elif q_type == "texte":
            return self.ask_text_question(question)
        else:
            return self.ask_text_question(question)

    def run_questionnaire(self):
        """Lance le questionnaire complet."""
        self.clear_screen()
        self.print_header()

        print("📋 Ce questionnaire va vous aider à identifier le projet")
        print("   entrepreneurial le plus adapté à votre profil.")
        print()
        print("💡 Conseils:")
        print("   • Répondez honnêtement pour des résultats pertinents")
        print("   • Tapez 'q' à tout moment pour quitter")
        print("   • Vos réponses seront sauvegardées")
        print()

        input("Appuyez sur Entrée pour commencer...")

        # Parcourir toutes les sections
        for section_id, section in QUESTIONS.items():
            self.clear_screen()
            self.print_header()
            self.print_section_header(section["titre"])

            for question in section["questions"]:
                reponse = self.ask_question(question)

                if reponse is None:  # User quit
                    print("\n👋 Questionnaire interrompu. Vos réponses ont été sauvegardées.")
                    self.save_responses()
                    return False

                self.reponses[question["id"]] = reponse

            print(f"\n✅ Section '{section['titre']}' terminée!")
            input("Appuyez sur Entrée pour continuer...")

        return True

    def save_responses(self):
        """Sauvegarde les réponses dans un fichier JSON."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.data_dir, f"reponses_{timestamp}.json")

        data = {
            "date": datetime.now().isoformat(),
            "reponses": self.reponses
        }

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"\n💾 Réponses sauvegardées: {filename}")
        return filename

    def load_responses(self, filename: str):
        """Charge des réponses depuis un fichier JSON."""
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.reponses = data.get("reponses", {})
        print(f"📂 Réponses chargées depuis: {filename}")

    def show_results(self):
        """Affiche les résultats de l'analyse."""
        self.clear_screen()
        self.print_header()

        print("🔄 Analyse de votre profil en cours...\n")

        # Générer le rapport
        report = generate_report(self.reponses, top_n=5)
        print(report)

        # Sauvegarder le rapport
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = os.path.join(self.data_dir, f"rapport_{timestamp}.txt")

        with open(report_file, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"\n💾 Rapport sauvegardé: {report_file}")

    def show_quick_results(self):
        """Affiche un résumé rapide des résultats."""
        resultats = analyze_profile(self.reponses)
        top_5 = resultats[:5]

        print("\n🏆 TOP 5 des projets recommandés:\n")
        for i, r in enumerate(top_5, 1):
            business = r["business"]
            print(f"   {i}. {business['nom']} - {r['pourcentage']}%")
            print(f"      💰 {business['revenus_potentiels']} | ⏱️ {business['temps_objectif_5k']}")
        print()

    def run(self):
        """Point d'entrée principal de l'application."""
        try:
            completed = self.run_questionnaire()

            if completed:
                self.save_responses()
                self.show_results()

                print("\n" + "=" * 60)
                print("🎉 Questionnaire terminé!")
                print("=" * 60)
                print("\n📌 Prochaines étapes suggérées:")
                print("   1. Relisez attentivement le rapport")
                print("   2. Approfondissez les 2-3 projets qui vous parlent le plus")
                print("   3. Faites une mini étude de marché")
                print("   4. Définissez votre premier objectif à 30 jours")
                print()
                print("💪 Bonne chance dans votre aventure entrepreneuriale!")
                print()

        except KeyboardInterrupt:
            print("\n\n👋 Au revoir!")
            self.save_responses()


def main():
    """Fonction principale."""
    app = CareerFinder()
    app.run()


if __name__ == "__main__":
    main()
