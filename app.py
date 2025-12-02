from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
import os
from database_config import DatabaseConfig
import json
from datetime import datetime

# Global variables for RAG chatbot service
RAG_AVAILABLE = False
get_rag_chatbot_response = None

# Import RAG chatbot service
try:
    from chatbot_service import get_rag_chatbot_response
    RAG_AVAILABLE = True
except ImportError:
    print("RAG chatbot service not available. Install required packages with: pip install scikit-learn numpy scipy")

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['DEBUG'] = True

# Initialize database
db = DatabaseConfig()

# Routes
@app.route('/')
def home():
    """Home page with introduction to Ayurveda and system purpose"""
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Patient Registration Page"""
    if request.method == 'POST':
        try:
            # Extract form data
            age = int(request.form['age'])
            gender = request.form['gender']
            prakriti_type = request.form.get('prakriti_type', '')
            current_symptoms = request.form.getlist('current_symptoms')
            symptom_severity = request.form['symptom_severity']
            treatment_history = request.form.get('treatment_history', '')
            effectiveness_rating = request.form.get('effectiveness_rating')
            practitioner_notes = request.form.get('practitioner_notes', '')
            
            # Convert symptoms list to string
            symptoms_str = ', '.join(current_symptoms) if current_symptoms else ''
            
            # Convert effectiveness rating to float if provided
            effectiveness_float = float(effectiveness_rating) if effectiveness_rating else None
            
            # Add patient profile to database
            result = db.add_patient_profile(
                age, gender, prakriti_type, symptoms_str, symptom_severity,
                treatment_history, effectiveness_float, practitioner_notes
            )
            
            if result:
                flash('Patient profile registered successfully!', 'success')
                return redirect(url_for('prakriti_quiz'))
            else:
                flash('Error registering patient profile. Please try again.', 'error')
                
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    
    # Get symptoms for the form
    try:
        symptoms = db.get_symptoms()
        if symptoms is None:
            symptoms = []
    except Exception as e:
        print(f"Error getting symptoms: {e}")
        # Provide mock data when database is not available
        symptoms = [
            {'symptom_id': 1, 'symptom_name': 'Headache', 'symptom_category': 'Neurological', 'description': 'Pain in the head or scalp area'},
            {'symptom_id': 2, 'symptom_name': 'Fatigue', 'symptom_category': 'General', 'description': 'Persistent tiredness and low energy'},
            {'symptom_id': 3, 'symptom_name': 'Indigestion', 'symptom_category': 'Digestive', 'description': 'Discomfort after eating; bloating'},
            {'symptom_id': 4, 'symptom_name': 'Joint Pain', 'symptom_category': 'Musculoskeletal', 'description': 'Pain, stiffness in joints'},
            {'symptom_id': 5, 'symptom_name': 'Insomnia', 'symptom_category': 'Neurological', 'description': 'Difficulty falling or staying asleep'}
        ]
    
    return render_template('register.html', symptoms=symptoms)

@app.route('/prakriti_quiz', methods=['GET', 'POST'])
def prakriti_quiz():
    """Prakriti Quiz Page"""
    if request.method == 'POST':
        try:
            # Calculate dosha scores based on quiz responses
            vata_score = 0
            pitta_score = 0
            kapha_score = 0
            
            # Process quiz responses (simplified scoring)
            for key, value in request.form.items():
                if key.startswith('question_'):
                    if value == 'vata':
                        vata_score += 1
                    elif value == 'pitta':
                        pitta_score += 1
                    elif value == 'kapha':
                        kapha_score += 1
            
            # Determine dominant dosha
            scores = {'vata': vata_score, 'pitta': pitta_score, 'kapha': kapha_score}
            dominant_dosha = max(scores, key=scores.get)
            
            # Get prakriti profile
            prakriti_profile = db.get_prakriti_profile_by_scores(vata_score, pitta_score, kapha_score)
            
            if not prakriti_profile:
                # Create a basic profile if exact match not found
                constitution_type = f"Mixed {dominant_dosha.title()}"
                prakriti_profile = [{
                    'dominant_dosha': dominant_dosha,
                    'constitution_type': constitution_type,
                    'characteristics': f"Based on your responses, you show {dominant_dosha} dominance.",
                    'common_ailments': "Consult with an Ayurvedic practitioner for specific recommendations.",
                    'recommended_lifestyle': "Follow {dominant_dosha}-balancing lifestyle practices."
                }]
            
            # Store in session for later use
            session['prakriti_results'] = {
                'vata_score': vata_score,
                'pitta_score': pitta_score,
                'kapha_score': kapha_score,
                'dominant_dosha': dominant_dosha,
                'profile': prakriti_profile[0] if prakriti_profile else None
            }
            
            flash('Prakriti assessment completed successfully!', 'success')
            return render_template('prakriti_results.html', 
                                 vata_score=vata_score, 
                                 pitta_score=pitta_score, 
                                 kapha_score=kapha_score,
                                 dominant_dosha=dominant_dosha,
                                 profile=prakriti_profile[0] if prakriti_profile else None)
            
        except Exception as e:
            flash(f'Error processing quiz: {str(e)}', 'error')
    
    return render_template('prakriti_quiz.html')

@app.route('/symptom_entry', methods=['GET', 'POST'])
def symptom_entry():
    """Symptom Entry Page"""
    if request.method == 'POST':
        try:
            selected_symptoms = request.form.getlist('symptoms')
            symptom_severities = {}
            
            # Get severity for each symptom
            for symptom in selected_symptoms:
                severity_key = f'severity_{symptom}'
                if severity_key in request.form:
                    symptom_severities[symptom] = request.form[severity_key]
            
            # Store in session
            session['selected_symptoms'] = selected_symptoms
            session['symptom_severities'] = symptom_severities
            
            flash('Symptoms recorded successfully!', 'success')
            return redirect(url_for('recommendations'))
            
        except Exception as e:
            flash(f'Error recording symptoms: {str(e)}', 'error')
    
    try:
        symptoms = db.get_symptoms()
        if symptoms is None:
            symptoms = []
    except Exception as e:
        print(f"Error getting symptoms: {e}")
        # Provide mock data when database is not available
        symptoms = [
            {'symptom_id': 1, 'symptom_name': 'Headache', 'symptom_category': 'Neurological', 'description': 'Pain in the head or scalp area'},
            {'symptom_id': 2, 'symptom_name': 'Fatigue', 'symptom_category': 'General', 'description': 'Persistent tiredness and low energy'},
            {'symptom_id': 3, 'symptom_name': 'Indigestion', 'symptom_category': 'Digestive', 'description': 'Discomfort after eating; bloating'},
            {'symptom_id': 4, 'symptom_name': 'Joint Pain', 'symptom_category': 'Musculoskeletal', 'description': 'Pain, stiffness in joints'},
            {'symptom_id': 5, 'symptom_name': 'Insomnia', 'symptom_category': 'Neurological', 'description': 'Difficulty falling or staying asleep'},
            {'symptom_id': 6, 'symptom_name': 'Cough', 'symptom_category': 'Respiratory', 'description': 'Expulsion of air with sound, may be dry/productive'},
            {'symptom_id': 7, 'symptom_name': 'Skin Rash', 'symptom_category': 'Dermatological', 'description': 'Red, itchy skin patches'},
            {'symptom_id': 8, 'symptom_name': 'Fever', 'symptom_category': 'Infectious', 'description': 'Raised body temperature often with malaise'},
            {'symptom_id': 9, 'symptom_name': 'Constipation', 'symptom_category': 'Digestive', 'description': 'Infrequent or difficult bowel movements'},
            {'symptom_id': 10, 'symptom_name': 'Acidity', 'symptom_category': 'Digestive', 'description': 'Burning sensation in stomach/oesophagus'}
        ]
    
    return render_template('symptom_entry.html', symptoms=symptoms)

@app.route('/recommendations')
def recommendations():
    """Recommendations Page - displays herb recommendations based on symptoms and prakriti"""
    try:
        # Get symptoms from session
        selected_symptoms = session.get('selected_symptoms', [])
        symptom_severities = session.get('symptom_severities', {})
        prakriti_results = session.get('prakriti_results', {})
        
        if not selected_symptoms:
            # Provide mock recommendations when no symptoms are selected
            mock_recommendations = [
                {
                    'herb_id': 1,
                    'herb_name_english': 'Ashwagandha',
                    'herb_name_sanskrit': 'Ashwagandha',
                    'scientific_name': 'Withania somnifera',
                    'rasa': 'Bitter',
                    'virya': 'Hot',
                    'vipaka': 'Sweet',
                    'prabhava': 'Rasayana (rejuvenator)',
                    'vata_effect': 'Balances Vata',
                    'pitta_effect': 'May increase Pitta in excess',
                    'kapha_effect': 'Reduces Kapha',
                    'part_used': 'Root',
                    'dosage': '3-6g daily',
                    'preparation_method': 'Powder/decoction',
                    'contraindications': 'Avoid in pregnancy & high fever',
                    'description': 'Stress adaptogen; increases strength and stamina',
                    'effectiveness_score': 0.85
                },
                {
                    'herb_id': 2,
                    'herb_name_english': 'Tulsi',
                    'herb_name_sanskrit': 'Tulasī',
                    'scientific_name': 'Ocimum tenuiflorum',
                    'rasa': 'Pungent',
                    'virya': 'Hot',
                    'vipaka': 'Sweet',
                    'prabhava': 'Immunity enhancer',
                    'vata_effect': 'Balances Vata',
                    'pitta_effect': 'Reduces Pitta',
                    'kapha_effect': 'Reduces Kapha',
                    'part_used': 'Leaves',
                    'dosage': '5-10 leaves or 1-2g powder',
                    'preparation_method': 'Infusion/decoction',
                    'contraindications': 'None common (use caution in pregnancy)',
                    'description': 'Anti-microbial and respiratory support',
                    'effectiveness_score': 0.80
                }
            ]
            return render_template('recommendations.html', 
                                 recommendations=mock_recommendations,
                                 selected_symptoms=[],
                                 symptom_severities={},
                                 prakriti_results=prakriti_results)
        
        # Get herb recommendations for each symptom
        recommendations = []
        for symptom_id in selected_symptoms:
            herbs = db.get_herbs_for_symptom(symptom_id)
            if herbs:
                recommendations.extend(herbs)
        
        # Remove duplicates and sort by effectiveness
        unique_herbs = {}
        for herb in recommendations:
            herb_id = herb['herb_id']
            if herb_id not in unique_herbs or herb['effectiveness_score'] > unique_herbs[herb_id]['effectiveness_score']:
                unique_herbs[herb_id] = herb
        
        recommendations = list(unique_herbs.values())
        recommendations.sort(key=lambda x: x['effectiveness_score'], reverse=True)
        
        return render_template('recommendations.html', 
                             recommendations=recommendations,
                             selected_symptoms=selected_symptoms,
                             symptom_severities=symptom_severities,
                             prakriti_results=prakriti_results)
        
    except Exception as e:
        flash(f'Error generating recommendations: {str(e)}', 'error')
        return redirect(url_for('home'))

@app.route('/herb_details/<int:herb_id>')
def herb_details(herb_id):
    """Herb Details Page - displays detailed information about a specific herb"""
    try:
        # Get herb details
        herbs = db.get_herbs()
        herb = next((h for h in herbs if h['herb_id'] == herb_id), None)
        
        if not herb:
            flash('Herb not found.', 'error')
            return redirect(url_for('herbs'))
        
        # Get symptoms this herb can help with
        symptoms = db.get_symptoms_for_herb(herb_id)
        
        return render_template('herb_details.html', herb=herb, symptoms=symptoms)
        
    except Exception as e:
        flash(f'Error loading herb details: {str(e)}', 'error')
        return redirect(url_for('herbs'))

@app.route('/herbs')
def herbs():
    """Herbs Page - displays all available herbs"""
    try:
        herbs_list = db.get_herbs()
        if herbs_list is None:
            herbs_list = []
    except Exception as e:
        print(f"Error loading herbs: {e}")
        herbs_list = []
    
    # Provide mock data when database is not available
    if not herbs_list:
        herbs_list = [
            {
                'herb_id': 1,
                'herb_name_english': 'Ashwagandha',
                'herb_name_sanskrit': 'Ashwagandha',
                'scientific_name': 'Withania somnifera',
                'rasa': 'Bitter',
                'virya': 'Hot',
                'vipaka': 'Sweet',
                'prabhava': 'Rasayana (rejuvenator)',
                'vata_effect': 'Balances Vata',
                'pitta_effect': 'May increase Pitta in excess',
                'kapha_effect': 'Reduces Kapha',
                'part_used': 'Root',
                'dosage': '3-6g daily',
                'preparation_method': 'Powder/decoction',
                'contraindications': 'Avoid in pregnancy & high fever',
                'description': 'Stress adaptogen; increases strength and stamina'
            },
            {
                'herb_id': 2,
                'herb_name_english': 'Tulsi',
                'herb_name_sanskrit': 'Tulasī',
                'scientific_name': 'Ocimum tenuiflorum',
                'rasa': 'Pungent',
                'virya': 'Hot',
                'vipaka': 'Sweet',
                'prabhava': 'Immunity enhancer',
                'vata_effect': 'Balances Vata',
                'pitta_effect': 'Reduces Pitta',
                'kapha_effect': 'Reduces Kapha',
                'part_used': 'Leaves',
                'dosage': '5-10 leaves or 1-2g powder',
                'preparation_method': 'Infusion/decoction',
                'contraindications': 'None common (use caution in pregnancy)',
                'description': 'Anti-microbial and respiratory support'
            },
            {
                'herb_id': 3,
                'herb_name_english': 'Triphala',
                'herb_name_sanskrit': 'Triphala',
                'scientific_name': 'Mixture of Emblica/Terminalia chebula/Terminalia bellirica',
                'rasa': 'Astringent',
                'virya': 'Mild Hot',
                'vipaka': 'Sweet',
                'prabhava': 'Detoxifier',
                'vata_effect': 'Balances Vata',
                'pitta_effect': 'Balances Pitta',
                'kapha_effect': 'Balances Kapha',
                'part_used': 'Fruits (three)',
                'dosage': '1-3g daily',
                'preparation_method': 'Powder',
                'contraindications': 'Caution in diarrhea',
                'description': 'Digestive tonic and mild laxative'
            }
        ]
    
    return render_template('herbs.html', herbs=herbs_list)

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    """Feedback Page - collects user feedback"""
    if request.method == 'POST':
        try:
            feedback_text = request.form['feedback']
            rating = request.form.get('rating', 0)
            user_type = request.form.get('user_type', 'patient')
            
            # Store feedback in database (you might want to create a feedback table)
            # For now, we'll just show a success message
            flash('Thank you for your feedback!', 'success')
            return redirect(url_for('home'))
            
        except Exception as e:
            flash(f'Error submitting feedback: {str(e)}', 'error')
    
    return render_template('feedback.html')

@app.route('/admin')
def admin():
    """Admin Data Entry Page - CRUD operations for herbs/symptoms/formulations"""
    try:
        herbs_list = db.get_herbs()
        symptoms_list = db.get_symptoms()
        formulations_list = db.get_formulations()
        
        return render_template('admin.html', 
                             herbs=herbs_list, 
                             symptoms=symptoms_list, 
                             formulations=formulations_list)
    except Exception as e:
        flash(f'Error loading admin data: {str(e)}', 'error')
        return render_template('admin.html', herbs=[], symptoms=[], formulations=[])

@app.route('/chatbot')
def chatbot():
    """Chatbot interface page"""
    return render_template('chatbot.html')

# API routes for AJAX requests
@app.route('/api/recommend', methods=['POST'])
def api_recommend():
    """API endpoint for getting recommendations (for future GNN integration)"""
    try:
        data = request.get_json()
        symptoms = data.get('symptoms', [])
        prakriti_type = data.get('prakriti_type', '')
        
        # For now, return mock recommendations
        # This is where the GNN model will be integrated later
        mock_recommendations = [
            {
                'herb_name': 'Ashwagandha',
                'dosage': '3-6g daily',
                'reason': 'Excellent for stress and fatigue',
                'contraindications': 'Avoid in pregnancy and high fever'
            },
            {
                'herb_name': 'Tulsi',
                'dosage': '5-10 leaves or 1-2g powder',
                'reason': 'Great for respiratory health',
                'contraindications': 'None common'
            }
        ]
        
        return jsonify({
            'success': True,
            'recommendations': mock_recommendations
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/symptoms')
def api_symptoms():
    """API endpoint to get all symptoms"""
    try:
        symptoms = db.get_symptoms()
        return jsonify({
            'success': True,
            'symptoms': symptoms
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/herbs')
def api_herbs():
    """API endpoint to get all herbs"""
    try:
        herbs = db.get_herbs()
        return jsonify({
            'success': True,
            'herbs': herbs
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """API endpoint for chatbot responses"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').lower()
        
        # Simple rule-based chatbot responses
        response = get_chatbot_response(user_message)
        
        return jsonify({
            'success': True,
            'response': response
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def get_chatbot_response(message):
    """Generate chatbot response based on user message"""
    message = message.lower().strip()
    
    # If RAG is available, use it for complex queries
    if RAG_AVAILABLE and get_rag_chatbot_response is not None and len(message) > 10:
        # Use RAG for detailed questions
        try:
            rag_response = get_rag_chatbot_response(message) if get_rag_chatbot_response is not None else None
            if rag_response and not rag_response.startswith("I don't have specific information"):
                return rag_response
        except Exception as e:
            print(f"Error using RAG chatbot: {e}")
    
    # Greeting responses
    if any(greeting in message for greeting in ['hello', 'hi', 'hey', 'namaste']):
        return "Hello! I'm your Ayurvedic assistant. How can I help you today? You can ask me about herbs, symptoms, or your Prakriti type."
    
    # Help responses
    if any(help_word in message for help_word in ['help', 'what can you do', 'assist']):
        return "I can help you with:<br>• Finding herbs for your symptoms<br>• Understanding Ayurvedic concepts like Doshas (Vata, Pitta, Kapha)<br>• Explaining herb properties and benefits<br>• Providing wellness tips<br>• Answering questions about Ayurvedic principles<br>Just ask me anything about Ayurveda!"
    
    # Prakriti/Vata/Pitta/Kapha related
    if any(word in message for word in ['prakriti', 'constitution']):
        return "Prakriti is your unique Ayurvedic constitution determined by the balance of Vata, Pitta, and Kapha energies. It's your natural state of balance that influences your physical and mental characteristics. Understanding your Prakriti helps personalize your health and wellness approach."
    
    if 'vata' in message:
        return "Vata is one of the three Doshas in Ayurveda, composed of Air and Ether elements. It governs movement, breathing, nerve impulses, and elimination. When balanced, Vata promotes creativity and vitality. When imbalanced, it can cause anxiety, insomnia, and digestive issues. Balancing Vata involves warm, nourishing foods and regular routines."
    
    if 'pitta' in message:
        return "Pitta is one of the three Doshas in Ayurveda, composed of Fire and Water elements. It governs digestion, metabolism, and transformation in the body. When balanced, Pitta promotes intelligence and focus. When imbalanced, it can cause anger, acidity, and inflammation. Cooling foods and activities help balance Pitta."
    
    if 'kapha' in message:
        return "Kapha is one of the three Doshas in Ayurveda, composed of Earth and Water elements. It governs structure, stability, and immunity. When balanced, Kapha promotes strength and calmness. When imbalanced, it can cause weight gain, congestion, and lethargy. Light, warming foods and stimulating activities help balance Kapha."
    
    # Symptom related
    if any(symptom_word in message for symptom_word in ['symptom', 'feel', 'pain', 'ache', 'sick', 'headache', 'fatigue', 'acidity']):
        return "I can help you understand symptoms from an Ayurvedic perspective. For example, headaches are often related to Pitta imbalance, fatigue to Vata imbalance, and acidity to Pitta imbalance. Different herbs can help balance these conditions. Try asking about specific symptoms like 'What helps with headaches?' or 'How to reduce acidity naturally?'"
    
    # Herb related
    if any(herb_word in message for herb_word in ['herb', 'medicine', 'remedy', 'treatment', 'ashwagandha', 'tulsi', 'triphala']):
        if 'ashwagandha' in message:
            return "Ashwagandha (Withania somnifera) is a powerful adaptogenic herb that helps the body adapt to stress. It's particularly beneficial for Vata imbalance, reduces fatigue, improves sleep quality, and enhances vitality. Typical dosage is 3-6g daily as powder or 1-2 capsules. It's especially helpful for those experiencing stress, anxiety, or exhaustion."
        elif 'tulsi' in message:
            return "Tulsi (Holy Basil, Ocimum tenuiflorum) is revered in Ayurveda for its immune-enhancing properties. It helps with respiratory issues, reduces stress, and balances Kapha and Vata. You can consume 5-10 fresh leaves daily or as tea. Tulsi is excellent for colds, coughs, and respiratory infections."
        elif 'triphala' in message:
            return "Triphala is a traditional Ayurvedic formula of three fruits: Amalaki, Bibhitaki, and Haritaki. It's a gentle detoxifier that balances all three Doshas, particularly effective for digestive health and natural cleansing. Typical dosage is 1-3g daily before bed. It's excellent for improving digestion and gentle bowel regulation."
        else:
            return "Ayurveda offers many healing herbs with specific properties. Popular herbs include Ashwagandha for stress relief, Tulsi for immunity, Triphala for digestion, Brahmi for memory, and Turmeric for inflammation. Each herb has unique tastes (Rasa), energies (Virya), and post-digestive effects (Vipaka) that influence its actions."
    
    # Navigation
    if 'navigate' in message or 'find' in message:
        return "You can explore our Ayurvedic resources:<br>• Take the Prakriti Quiz to discover your constitution<br>• Check Symptoms to identify health concerns<br>• View Herbs to learn about medicinal plants<br>• Register to save your health journey<br>All these features help personalize your Ayurvedic wellness experience."
    
    # Default response
    # If RAG is available, try it as a fallback
    if RAG_AVAILABLE and get_rag_chatbot_response is not None:
        try:
            rag_response = get_rag_chatbot_response(message) if get_rag_chatbot_response is not None else None
            if rag_response and not rag_response.startswith("I don't have specific information"):
                return rag_response
        except Exception as e:
            print(f"Error using RAG chatbot: {e}")
    
    return "I'm here to help with your Ayurvedic wellness journey. You can ask me specific questions about herbs, symptoms, or Doshas (Vata, Pitta, Kapha). For example:<br>• 'What helps with headaches?'<br>• 'Tell me about Pitta dosha'<br>• 'Benefits of Ashwagandha'<br>• 'How to balance Vata?'"

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)