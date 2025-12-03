from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    redirect,
    url_for,
    flash,
    session,
)
from database_config import DatabaseConfig
import json

app = Flask(__name__)
app.secret_key = "ayurveda_secret_key"  # Change this in production

# Initialize Database Connection
db = DatabaseConfig()

# --- ROUTES ---


@app.route("/")
def home():
    """Home page."""
    return render_template("home.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """
    Patient Registration.
    - Saves profile to Neo4j.
    - Redirects to Symptom Entry (if Prakriti known).
    - Redirects to Procedure Page (if Prakriti unknown).
    """
    if request.method == "POST":
        try:
            # Extract form data
            age = int(request.form["age"])
            gender = request.form["gender"]
            prakriti_type = request.form.get("prakriti_type", "")

            # Note: Current symptoms in this form are basic. Detailed entry happens next.
            current_symptoms = request.form.getlist("current_symptoms")
            symptoms_str = ", ".join(current_symptoms) if current_symptoms else ""

            symptom_severity = request.form["symptom_severity"]
            treatment_history = request.form.get("treatment_history", "")

            effectiveness = request.form.get("effectiveness_rating")
            effectiveness_float = float(effectiveness) if effectiveness else 0.0

            practitioner_notes = request.form.get("practitioner_notes", "")

            # Save to Neo4j using existing method signature
            db.add_patient_profile(
                age=age,
                gender=gender,
                prakriti_type=prakriti_type,
                symptoms=symptoms_str,
                severity=symptom_severity,
                treatment_history=treatment_history,
                effectiveness=effectiveness_float,
                practitioner_notes=practitioner_notes,
            )

            # Store critical info in Session for the recommendation engine
            session["prakriti"] = prakriti_type

            flash("Profile registered successfully!", "success")

            # LOGIC: Where to go next?
            if prakriti_type and prakriti_type != "":
                return redirect(url_for("symptom_entry"))
            else:
                return redirect(url_for("prakriti_quiz"))

        except Exception as e:
            flash(f"Error registering: {str(e)}", "error")

    # GET request: Load symptoms for the checkboxes
    try:
        symptoms = db.get_symptoms()
        if symptoms is None:
            symptoms = []
    except:
        symptoms = []

    return render_template("register.html", symptoms=symptoms)


@app.route("/prakriti_quiz")
def prakriti_quiz():
    """
    Informational Page: Official Assessment Procedure.
    No data entry here.
    """
    return render_template("prakriti_quiz.html")


@app.route("/symptom_entry", methods=["GET", "POST"])
def symptom_entry():
    """
    Detailed Symptom Selection.
    """
    if request.method == "POST":
        selected_symptoms = request.form.getlist("symptoms")

        # Save to session so we can query DB in the next step
        session["selected_symptoms"] = selected_symptoms

        # Also capture severities if needed, though user code didn't explicitly handle them in session logic
        # We'll stick to user's simple logic for now but might want to add them back if templates need them

        flash("Symptoms recorded. Generating recommendations...", "success")
        return redirect(url_for("recommendations"))

    # Load all symptoms from Neo4j to populate the form
    try:
        symptoms = db.get_symptoms()
        if symptoms is None:
            symptoms = []
    except Exception as e:
        print(f"DB Error: {e}")
        symptoms = []

    return render_template("symptom_entry.html", symptoms=symptoms)


@app.route("/recommendations")
def recommendations():
    """
    The Core Engine: Fetches Herbs from Neo4j based on Session Data.
    """
    selected_symptoms = session.get("selected_symptoms", [])
    user_prakriti = session.get("prakriti", "")

    final_recommendations = []

    try:
        if selected_symptoms:
            # 1. Iterate through symptoms and query Neo4j
            for symptom_name in selected_symptoms:
                # This calls the method we wrote in database_config.py
                # Note: get_herbs_for_symptom handles both ID and Name lookup
                herbs = db.get_herbs_for_symptom(symptom_name)

                # 2. Filter or Flag based on Prakriti (Basic Logic)
                for herb in herbs:
                    # Add a 'suitability' flag if it matches the user's Dosha
                    # We check if user_prakriti is mentioned in the herb's effects
                    # This is a simple heuristic
                    is_match = False
                    if user_prakriti:
                        prakriti_lower = user_prakriti.lower()
                        if (
                            prakriti_lower in herb.get("vata_effect", "").lower()
                            or prakriti_lower in herb.get("pitta_effect", "").lower()
                            or prakriti_lower in herb.get("kapha_effect", "").lower()
                        ):
                            is_match = True

                    herb["is_perfect_match"] = is_match
                    final_recommendations.append(herb)

            # 3. Deduplicate (If an herb treats multiple symptoms, show it once)
            # Deduplication by herb_name_english
            seen = set()
            unique_recs = []
            for h in final_recommendations:
                name = h.get("herb_name_english")
                if name and name not in seen:
                    unique_recs.append(h)
                    seen.add(name)

            final_recommendations = unique_recs

            # Sort by effectiveness if available
            final_recommendations.sort(
                key=lambda x: x.get("effectiveness_score", 0), reverse=True
            )

    except Exception as e:
        flash(f"Error fetching recommendations: {e}", "error")

    # Construct a minimal prakriti_results object for the template if possible
    prakriti_results = None
    if user_prakriti:
        prakriti_results = {
            "dominant_dosha": user_prakriti,
            "vata_score": "-",  # Scores not available in this flow
            "pitta_score": "-",
            "kapha_score": "-",
        }

    return render_template(
        "recommendations.html",
        recommendations=final_recommendations,
        prakriti_results=prakriti_results,
        selected_symptoms=selected_symptoms,
    )


@app.route("/herbs")
def herbs():
    """List all herbs."""
    try:
        # Use existing method to get correct fields for template
        herbs_list = db.get_herbs()
        if herbs_list is None:
            herbs_list = []
    except Exception as e:
        herbs_list = []
        print(e)

    return render_template("herbs.html", herbs=herbs_list)


@app.route("/herb_details/<int:herb_id>")
def herb_details(herb_id):
    """Herb Details Page - displays detailed information about a specific herb"""
    try:
        # Get herb details
        herbs = db.get_herbs()
        herb = next((h for h in herbs if h["herb_id"] == herb_id), None)

        if not herb:
            flash("Herb not found.", "error")
            return redirect(url_for("herbs"))

        # Get symptoms this herb can help with
        symptoms = db.get_symptoms_for_herb(herb_id)

        return render_template("herb_details.html", herb=herb, symptoms=symptoms)

    except Exception as e:
        flash(f"Error loading herb details: {str(e)}", "error")
        return redirect(url_for("herbs"))


@app.route("/feedback", methods=["GET", "POST"])
def feedback():
    """Feedback Page - collects user feedback"""
    if request.method == "POST":
        try:
            flash("Thank you for your feedback!", "success")
            return redirect(url_for("home"))
        except Exception as e:
            flash(f"Error submitting feedback: {str(e)}", "error")
    return render_template("feedback.html")


# --- CHATBOT ---
@app.route("/chatbot")
def chatbot():
    return render_template("chatbot.html")


@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json()
    msg = data.get("message", "").lower()

    # Simple Neo4j-aware response
    response = "I am connected to the Knowledge Graph. Ask me about herbs!"
    if "ashwagandha" in msg:
        response = "Ashwagandha is a powerful Rasayana herb known for reducing stress (Vata balancing)."

    return jsonify({"success": True, "response": response})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
