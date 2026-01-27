# 🥘 Rezeptfinder Web App

Eine Webanwendung mit **Flask**, die es ermöglicht, Rezepte anhand von Zutaten über die **Spoonacular API** zu suchen, Favoriten zu speichern und eine Einkaufsliste zu verwalten.

---

## 📌 Funktionen

- 🔍 Suche von Rezepten
- ⭐ Hinzufügen von Rezepten zu den Favoriten  
- 🛒 Einkaufsliste mit Markierung erledigter Einträge  
- 🧑‍🍳 Eigene Rezepte manuell hinzufügen  
- 📄 Detailansicht einzelner Rezepte  
- 🎥 Kurze Videodemonstration des Programms (siehe unten)

---

### ⚙️ Installation und Ausführung
- Repository klonen
bash
git clone https://github.com/link.git
cd <projektordner>
Anwendung starten

-Abhängigkeiten installieren

-Im Projektordner folgenden Befehl ausführen:

python app.py

--------
### Backend Routes

GET / – Renders the home page with the recipe search interface.

POST / – Handles recipe searches by ingredients via form submission.

GET /about – Displays the "About Us" information page.

GET /contact – Renders the contact form page.

POST /contact – Processes and submits the contact form data.

GET /recipe/<recipe_id> – Displays detailed information for a specific recipe.

POST /api/search – API endpoint that returns recipe search results in JSON format.

https://github.com/user-attachments/assets/45d45c47-995a-4eb3-a3a0-510512ac527e

