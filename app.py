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
import os
import json
from datetime import datetime
from database_config import DatabaseConfig
from ai_engine.predictor import AyurvedaPredictor
from ai_engine.inference import AyurvedicAI

# Initialize the Brain
try:
    ai_engine = AyurvedicAI()
except Exception as e:
    print(f"Warning: Could not load AI Engine. {e}")
    ai_engine = None

# Global variables for RAG chatbot service
RAG_AVAILABLE = False
get_rag_chatbot_response = None

# Import RAG chatbot service
try:
    from chatbot_service import get_rag_chatbot_response

    RAG_AVAILABLE = True
except ImportError:
    print(
        "RAG chatbot service not available. Install required packages with: pip install scikit-learn numpy scipy"
    )

# Import RL Service
try:
    from rl_service import rl_service

    RL_AVAILABLE = True
except ImportError:
    print("RL service not available.")
    RL_AVAILABLE = False

app = Flask(__name__)
app.secret_key = "ayurveda_secret_key"  # Change this in production
app.config["DEBUG"] = True

# Initialize Database Connection
db = DatabaseConfig()

# Initialize AI Brain
# Ensure paths are correct relative to app.py
# ai_brain = AyurvedaPredictor(
#     model_path="ai_engine/ayurveda_gnn_model.pth",
#     data_path="ai_engine/graph_data.pt",
#     artifacts_path="ai_engine/gnn_artifacts.pkl",
# )

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
            state = request.form.get("state", "")
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
                state=state,
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

        # Also capture severities if needed
        symptom_severities = {}
        for symptom in selected_symptoms:
            severity_key = f"severity_{symptom}"
            if severity_key in request.form:
                symptom_severities[symptom] = request.form[severity_key]
        session["symptom_severities"] = symptom_severities

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


@app.route("/recommendations", methods=["GET", "POST"])
def recommendations():
    """
    Recommendations Page.
    Fetches recommendations using the Graph Database.
    """
    if request.method == "POST":
        # Get symptoms from form
        selected_symptoms = request.form.getlist("symptoms")

        # Save to session for persistence
        session["selected_symptoms"] = selected_symptoms

    else:  # GET request
        # Retrieve from session
        selected_symptoms = session.get("selected_symptoms", [])

    if not selected_symptoms:
        # If no symptoms selected (or session expired), show empty state
        return render_template("recommendations.html", herbs=[])

    try:
        # Get recommendations from AI Engine
        recommendations = []
        seen_herbs = set()

        if ai_engine:
            for symptom in selected_symptoms:
                # Get AI results for each symptom
                results = ai_engine.get_recommendations(symptom, top_k=5)

                for res in results:
                    if res["name"] not in seen_herbs:
                        recommendations.append(res)
                        seen_herbs.add(res["name"])

            # Sort by score descending
            recommendations.sort(key=lambda x: x["score"], reverse=True)

        else:
            # Fallback if AI engine failed to load
            print("AI Engine not available, falling back to DB")
            recommendations = db.get_graph_recommendations(selected_symptoms)

        return render_template("recommendations.html", herbs=recommendations)

    except Exception as e:
        print(f"Error getting recommendations: {e}")
        flash(f"Error generating recommendations: {str(e)}", "error")
        return render_template("recommendations.html", herbs=[])


@app.route("/get_ai_recommendations", methods=["POST"])
def get_ai_recommendations():
    if not ai_engine:
        return jsonify({"error": "AI Engine not active"}), 503

    data = request.json
    symptom = data.get("symptom")  # e.g., "Insomnia"
    prakriti = data.get("prakriti")  # e.g., "Vata"

    # Get results from the Brain
    results = ai_engine.get_recommendations(symptom, prakriti)

    # If AI finds nothing, maybe fallback to DB query here?

    return jsonify(results)


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


@app.route("/admin")
def admin():
    """Admin Data Entry Page - CRUD operations for herbs/symptoms/formulations"""
    try:
        herbs_list = db.get_herbs()
        symptoms_list = db.get_symptoms()
        formulations_list = db.get_formulations()

        return render_template(
            "admin.html",
            herbs=herbs_list,
            symptoms=symptoms_list,
            formulations=formulations_list,
        )
    except Exception as e:
        flash(f"Error loading admin data: {str(e)}", "error")
        return render_template("admin.html", herbs=[], symptoms=[], formulations=[])


@app.route("/chatbot")
def chatbot():
    """Chatbot interface page"""
    return render_template("chatbot.html")


# --- API ROUTES ---


# @app.route("/api/recommend", methods=["POST"])
@app.route("/api/recommend", methods=["POST"])
def api_recommend():
    """
    Endpoint to get herb recommendations.
    Current Mode: Graph Database Query (Neo4j)
    Future Mode: GNN Inference
    """
    try:
        data = request.get_json()
        symptoms = data.get("symptoms", [])  # List of Symptom IDs (e.g., ['1', '5'])
        prakriti_type = data.get("prakriti_type", "")

        # 1. FETCH FROM DATABASE (The "Rule-Based" Fallback)
        recommendations = db.get_graph_recommendations(symptoms)

        # 2. Fallback if database returns nothing
        if not recommendations:
            return jsonify(
                {
                    "success": True,
                    "source": "fallback_rule",
                    "recommendations": [
                        {
                            "herb_name": "Triphala",
                            "dosage": "1 tsp with warm water",
                            "reason": "General detoxification and balance (Default recommendation)",
                            "contraindications": "None",
                        }
                    ],
                }
            )

        return jsonify(
            {
                "success": True,
                "source": "neo4j_graph",  # Flag to let you know it came from DB
                "recommendations": recommendations,
            }
        )

    except Exception as e:
        print(f"Error in recommendation: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/symptoms")
def api_symptoms():
    """API endpoint to get all symptoms"""
    try:
        symptoms = db.get_symptoms()
        return jsonify({"success": True, "symptoms": symptoms})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/herbs")
def api_herbs():
    """API endpoint to get all herbs"""
    try:
        herbs = db.get_herbs()
        return jsonify({"success": True, "herbs": herbs})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/feedback/chat", methods=["POST"])
def api_chat_feedback():
    """API endpoint for chat feedback (RL training)"""
    try:
        data = request.get_json()
        query = data.get("query", "")
        action = data.get("action", 0)
        reward = data.get("reward", 0)  # 1 for positive, -1 for negative

        if RL_AVAILABLE:
            new_q = rl_service.update_feedback(query, action, reward)
            return jsonify({"success": True, "new_q": new_q})

        return jsonify({"success": False, "error": "RL not available"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/chat", methods=["POST"])
def api_chat():
    """API endpoint for chatbot responses"""
    try:
        data = request.get_json()
        user_message = data.get("message", "").lower()

        # Simple rule-based chatbot responses
        response = get_chatbot_response(user_message)

        return jsonify({"success": True, "response": response})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


def _get_rule_based_response(message):
    """Helper for rule-based responses"""
    if "vata" in message:
        return "Vata is one of the three Doshas in Ayurveda, composed of Air and Ether elements. It governs movement, breathing, nerve impulses, and elimination. When balanced, Vata promotes creativity and vitality. When imbalanced, it can cause anxiety, insomnia, and digestive issues. Balancing Vata involves warm, nourishing foods and regular routines."

    if "pitta" in message:
        return "Pitta is one of the three Doshas in Ayurveda, composed of Fire and Water elements. It governs digestion, metabolism, and transformation in the body. When balanced, Pitta promotes intelligence and focus. When imbalanced, it can cause anger, acidity, and inflammation. Cooling foods and activities help balance Pitta."

    if "kapha" in message:
        return "Kapha is one of the three Doshas in Ayurveda, composed of Earth and Water elements. It governs structure, stability, and immunity. When balanced, Kapha promotes strength and calmness. When imbalanced, it can cause weight gain, congestion, and lethargy. Light, warming foods and stimulating activities help balance Kapha."

    # Specific Symptom Advice
    if "headache" in message:
        return "For headaches, Ayurveda recommends cooling herbs like Brahmi and Sandalwood paste application. Drinking warm water and avoiding spicy foods can also help. If it's a migraine, it might be related to Pitta imbalance."

    if "acidity" in message or "heartburn" in message:
        return "For acidity, avoid spicy and sour foods. Cooling herbs like Amla, Coriander water, and Fennel seeds are very effective. Coconut water is also excellent for soothing the stomach lining."

    if "fatigue" in message or "tired" in message:
        return "Fatigue is often a sign of Vata imbalance. Ashwagandha is the best herb for boosting energy and vitality. Ensure you're getting enough rest and eating warm, nourishing foods."

    if "insomnia" in message or "sleep" in message:
        return "For better sleep, try drinking warm milk with a pinch of nutmeg before bed. Massaging your feet with warm sesame oil (Padabhyanga) is also very effective for calming Vata and inducing sleep."

    if "joint pain" in message or "arthritis" in message:
        return "Joint pain can be due to Vata aggravation. Turmeric milk (Golden Milk) is a powerful anti-inflammatory. Gentle yoga and applying warm Mahanarayan oil can also provide relief."

    # Herb related
    if any(
        herb_word in message
        for herb_word in [
            "herb",
            "medicine",
            "remedy",
            "treatment",
            "ashwagandha",
            "tulsi",
            "triphala",
        ]
    ):
        if "ashwagandha" in message:
            return "Ashwagandha (Withania somnifera) is a powerful adaptogenic herb that helps the body adapt to stress. It's particularly beneficial for Vata imbalance, reduces fatigue, improves sleep quality, and enhances vitality. Typical dosage is 3-6g daily as powder or 1-2 capsules. It's especially helpful for those experiencing stress, anxiety, or exhaustion."
        elif "tulsi" in message:
            return "Tulsi (Holy Basil, Ocimum tenuiflorum) is revered in Ayurveda for its immune-enhancing properties. It helps with respiratory issues, reduces stress, and balances Kapha and Vata. You can consume 5-10 fresh leaves daily or as tea. Tulsi is excellent for colds, coughs, and respiratory infections."
        elif "triphala" in message:
            return "Triphala is a traditional Ayurvedic formula of three fruits: Amalaki, Bibhitaki, and Haritaki. It's a gentle detoxifier that balances all three Doshas, particularly effective for digestive health and natural cleansing. Typical dosage is 1-3g daily before bed. It's excellent for improving digestion and gentle bowel regulation."
        else:
            return "Ayurveda offers many healing herbs with specific properties. Popular herbs include Ashwagandha for stress relief, Tulsi for immunity, Triphala for digestion, Brahmi for memory, and Turmeric for inflammation. Each herb has unique tastes (Rasa), energies (Virya), and post-digestive effects (Vipaka) that influence its actions."

    # Generic Symptom Help (Fallback)
    if any(
        symptom_word in message
        for symptom_word in [
            "symptom",
            "feel",
            "pain",
            "ache",
            "sick",
            "illness",
            "disease",
        ]
    ):
        return "I can help you understand symptoms from an Ayurvedic perspective. For example, headaches are often related to Pitta imbalance, fatigue to Vata imbalance, and acidity to Pitta imbalance. Different herbs can help balance these conditions. Try asking about specific symptoms like 'What helps with headaches?' or 'How to reduce acidity naturally?'"

    # Navigation
    if "navigate" in message or "find" in message:
        return "You can explore our Ayurvedic resources:<br>• Take the Prakriti Quiz to discover your constitution<br>• Check Symptoms to identify health concerns<br>• View Herbs to learn about medicinal plants<br>• Register to save your health journey<br>All these features help personalize your Ayurvedic wellness experience."

    return None


def get_chatbot_response(message):
    """Generate chatbot response based on user message using RL"""
    message = message.lower().strip()

    # Default Action: 0 (RAG)
    action = 0
    if RL_AVAILABLE:
        action, _ = rl_service.get_action(message)
        print(f"RL Action Selected: {action}")

    rag_response = None
    rule_response = None

    # Execute based on action
    if action == 0:  # Prefer RAG
        if RAG_AVAILABLE and get_rag_chatbot_response is not None:
            try:
                rag_response = get_rag_chatbot_response(message)
                if rag_response and not rag_response.startswith(
                    "I don't have specific information"
                ):
                    return rag_response
            except Exception as e:
                print(f"RAG Error: {e}")

        # Fallback to rules if RAG failed
        rule_response = _get_rule_based_response(message)
        if rule_response:
            return rule_response

    elif action == 1:  # Prefer Rules
        rule_response = _get_rule_based_response(message)
        if rule_response:
            return rule_response

        # Fallback to RAG if rules failed
        if RAG_AVAILABLE and get_rag_chatbot_response is not None:
            try:
                rag_response = get_rag_chatbot_response(message)
                if rag_response and not rag_response.startswith(
                    "I don't have specific information"
                ):
                    return rag_response
            except Exception as e:
                print(f"RAG Error: {e}")

    # Action 2 or Fallback
    return "I'm here to help with your Ayurvedic wellness journey. You can ask me specific questions about herbs, symptoms, or Doshas (Vata, Pitta, Kapha). For example:<br>• 'What helps with headaches?'<br>• 'Tell me about Pitta dosha'<br>• 'Benefits of Ashwagandha'<br>• 'How to balance Vata?'"


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template("500.html"), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
