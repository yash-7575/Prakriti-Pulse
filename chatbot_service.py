"""
RAG Chatbot Service for Prakriti Pulse
Implements Retrieval-Augmented Generation for Ayurvedic herb recommendations
"""
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

# Import database functions with error handling
try:
    from database_config import (
        get_herbs, get_symptoms, get_prakriti_profiles, 
        get_herb_symptom_relationships, get_formulations
    )
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False
    print("Database module not available, using mock data")
    # Define mock functions that return None
    def get_herbs():
        return None
    def get_symptoms():
        return None
    def get_prakriti_profiles():
        return None
    def get_herb_symptom_relationships():
        return None

class RAGChatbotService:
    """RAG Chatbot Service for Ayurvedic recommendations"""
    
    def __init__(self):
        """Initialize the RAG chatbot service"""
        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            max_features=1000
        )
        self.knowledge_base = []
        self.knowledge_vectors = None
        self._build_knowledge_base()
    
    def _get_mock_data(self):
        """Get mock data when database is not available"""
        # Mock herbs data
        herbs = [
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
                'preparation_method': 'Powder/decoction',
                'dosage': '3-6g daily',
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
                'preparation_method': 'Infusion/decoction',
                'dosage': '5-10 leaves or 1-2g powder',
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
                'preparation_method': 'Powder',
                'dosage': '1-3g daily',
                'contraindications': 'Caution in diarrhea',
                'description': 'Digestive tonic and mild laxative'
            },
            {
                'herb_id': 4,
                'herb_name_english': 'Brahmi',
                'herb_name_sanskrit': 'Brahmī',
                'scientific_name': 'Bacopa monnieri',
                'rasa': 'Bitter',
                'virya': 'Cooling',
                'vipaka': 'Sweet',
                'prabhava': 'Medhya (memory enhancer)',
                'vata_effect': 'Calms Vata',
                'pitta_effect': 'Balances Pitta',
                'kapha_effect': 'Little effect on Kapha',
                'part_used': 'Leaves',
                'preparation_method': 'Extract/paste',
                'dosage': '250-500mg extract',
                'contraindications': 'Avoid high doses in pregnancy',
                'description': 'Used for cognitive support and mental clarity'
            },
            {
                'herb_id': 5,
                'herb_name_english': 'Turmeric',
                'herb_name_sanskrit': 'Haridra',
                'scientific_name': 'Curcuma longa',
                'rasa': 'Bitter, Pungent',
                'virya': 'Hot',
                'vipaka': 'Sweet',
                'prabhava': 'Kapha and Pitta reducer',
                'vata_effect': 'Balances Vata',
                'pitta_effect': 'Reduces Pitta',
                'kapha_effect': 'Reduces Kapha',
                'part_used': 'Rhizome',
                'preparation_method': 'Powder in milk',
                'dosage': '1-2g daily',
                'contraindications': 'Caution with gallstones',
                'description': 'Anti-inflammatory and antioxidant'
            }
        ]
        
        # Mock symptoms data
        symptoms = [
            {
                'symptom_id': 1,
                'symptom_name': 'Headache',
                'symptom_category': 'Neurological',
                'associated_dosha': 'Pitta',
                'body_system': 'Nervous system',
                'description': 'Pain located in head or scalp area'
            },
            {
                'symptom_id': 2,
                'symptom_name': 'Indigestion',
                'symptom_category': 'Digestive',
                'associated_dosha': 'Kapha',
                'body_system': 'Digestive system',
                'description': 'Discomfort after eating; bloating'
            },
            {
                'symptom_id': 3,
                'symptom_name': 'Fatigue',
                'symptom_category': 'General',
                'associated_dosha': 'Vata',
                'body_system': 'Whole body',
                'description': 'Persistent tiredness and low energy'
            },
            {
                'symptom_id': 4,
                'symptom_name': 'Acidity',
                'symptom_category': 'Digestive',
                'associated_dosha': 'Pitta',
                'body_system': 'Digestive system',
                'description': 'Burning sensation in stomach/oesophagus'
            },
            {
                'symptom_id': 5,
                'symptom_name': 'Joint Pain',
                'symptom_category': 'Musculoskeletal',
                'associated_dosha': 'Vata',
                'body_system': 'Skeletal system',
                'description': 'Pain, stiffness in joints'
            }
        ]
        
        # Mock prakriti profiles data
        prakriti_profiles = [
            {
                'profile_id': 1,
                'vata_score': 70,
                'pitta_score': 20,
                'kapha_score': 10,
                'dominant_dosha': 'Vata',
                'constitution_type': 'Single (Vata)',
                'characteristics': 'Thin build, variable appetite, creative, quick thinker',
                'common_ailments': 'Insomnia, gas, dryness, joint pain',
                'recommended_lifestyle': 'Warm routine, grounding foods, oil massage'
            },
            {
                'profile_id': 2,
                'vata_score': 20,
                'pitta_score': 75,
                'kapha_score': 5,
                'dominant_dosha': 'Pitta',
                'constitution_type': 'Single (Pitta)',
                'characteristics': 'Medium build, strong digestion, driven temperament',
                'common_ailments': 'Acidity, inflammation, skin rashes',
                'recommended_lifestyle': 'Cool foods, avoid spicy, regular rest'
            },
            {
                'profile_id': 3,
                'vata_score': 15,
                'pitta_score': 20,
                'kapha_score': 75,
                'dominant_dosha': 'Kapha',
                'constitution_type': 'Single (Kapha)',
                'characteristics': 'Sturdy build, calm, steady appetite',
                'common_ailments': 'Obesity, congestion, lethargy',
                'recommended_lifestyle': 'Stimulating activity, light diet, dry foods'
            }
        ]
        
        # Mock herb-symptom relationships
        relationships = [
            {
                'herb_id': 1,
                'symptom_id': 3,
                'herb_name_english': 'Ashwagandha',
                'symptom_name': 'Fatigue',
                'effectiveness_score': 0.85,
                'classical_reference': 'Charaka Samhita',
                'dosage_for_symptom': '3-6g daily',
                'preparation_method': 'Powder with warm milk',
                'duration_of_treatment': '4-6 weeks'
            },
            {
                'herb_id': 2,
                'symptom_id': 1,
                'herb_name_english': 'Tulsi',
                'symptom_name': 'Headache',
                'effectiveness_score': 0.75,
                'classical_reference': 'Sushruta Samhita',
                'dosage_for_symptom': '2-3 leaves or 1g powder',
                'preparation_method': 'Infusion',
                'duration_of_treatment': '1-2 weeks'
            },
            {
                'herb_id': 5,
                'symptom_id': 4,
                'herb_name_english': 'Turmeric',
                'symptom_name': 'Acidity',
                'effectiveness_score': 0.70,
                'classical_reference': 'Ashtanga Hridayam',
                'dosage_for_symptom': '1g with honey',
                'preparation_method': 'Powder with honey or milk',
                'duration_of_treatment': '2-3 weeks'
            }
        ]
        
        return herbs, symptoms, prakriti_profiles, relationships
    
    def _build_knowledge_base(self):
        """Build knowledge base from database or mock data"""
        try:
            # Get data from database or use mock data
            herbs_data = None
            symptoms_data = None
            profiles_data = None
            relationships_data = None
            
            if DATABASE_AVAILABLE:
                try:
                    herbs_data = get_herbs()
                    symptoms_data = get_symptoms()
                    profiles_data = get_prakriti_profiles()
                    relationships_data = get_herb_symptom_relationships()
                except Exception as e:
                    print(f"Database access error: {e}")
                    herbs_data = None
                    symptoms_data = None
                    profiles_data = None
                    relationships_data = None
            
            # If database is not available or failed, use mock data
            if herbs_data is None:
                herbs_data, symptoms_data, profiles_data, relationships_data = self._get_mock_data()
            
            # Process herbs
            if herbs_data:
                for herb in herbs_data:
                    # Create knowledge entry for each herb
                    entry = {
                        'type': 'herb',
                        'id': herb.get('herb_id', 0),
                        'name': herb.get('herb_name_english', ''),
                        'sanskrit_name': herb.get('herb_name_sanskrit', ''),
                        'scientific_name': herb.get('scientific_name', ''),
                        'rasa': herb.get('rasa', ''),
                        'virya': herb.get('virya', ''),
                        'vipaka': herb.get('vipaka', ''),
                        'prabhava': herb.get('prabhava', ''),
                        'vata_effect': herb.get('vata_effect', ''),
                        'pitta_effect': herb.get('pitta_effect', ''),
                        'kapha_effect': herb.get('kapha_effect', ''),
                        'part_used': herb.get('part_used', ''),
                        'preparation_method': herb.get('preparation_method', ''),
                        'dosage': herb.get('dosage', ''),
                        'contraindications': herb.get('contraindications', ''),
                        'description': herb.get('description', ''),
                        'text': self._create_herb_text(herb)
                    }
                    self.knowledge_base.append(entry)
            
            # Process symptoms
            if symptoms_data:
                for symptom in symptoms_data:
                    # Create knowledge entry for each symptom
                    entry = {
                        'type': 'symptom',
                        'id': symptom.get('symptom_id', 0),
                        'name': symptom.get('symptom_name', ''),
                        'category': symptom.get('symptom_category', ''),
                        'associated_dosha': symptom.get('associated_dosha', ''),
                        'body_system': symptom.get('body_system', ''),
                        'description': symptom.get('description', ''),
                        'text': self._create_symptom_text(symptom)
                    }
                    self.knowledge_base.append(entry)
            
            # Process prakriti profiles
            if profiles_data:
                for profile in profiles_data:
                    # Create knowledge entry for each prakriti profile
                    entry = {
                        'type': 'prakriti',
                        'id': profile.get('profile_id', 0),
                        'dominant_dosha': profile.get('dominant_dosha', ''),
                        'constitution_type': profile.get('constitution_type', ''),
                        'characteristics': profile.get('characteristics', ''),
                        'common_ailments': profile.get('common_ailments', ''),
                        'recommended_lifestyle': profile.get('recommended_lifestyle', ''),
                        'text': self._create_prakriti_text(profile)
                    }
                    self.knowledge_base.append(entry)
            
            # Process herb-symptom relationships
            if relationships_data:
                for rel in relationships_data:
                    # Create knowledge entry for each relationship
                    entry = {
                        'type': 'relationship',
                        'herb_id': rel.get('herb_id', 0),
                        'symptom_id': rel.get('symptom_id', 0),
                        'herb_name': rel.get('herb_name_english', rel.get('herb_name', '')),
                        'symptom_name': rel.get('symptom_name', ''),
                        'effectiveness_score': float(rel.get('effectiveness_score', 0)),
                        'classical_reference': rel.get('classical_reference', ''),
                        'dosage_for_symptom': rel.get('dosage_for_symptom', ''),
                        'preparation_method': rel.get('preparation_method', ''),
                        'duration_of_treatment': rel.get('duration_of_treatment', ''),
                        'text': self._create_relationship_text(rel)
                    }
                    self.knowledge_base.append(entry)
            
            # Vectorize the knowledge base
            if self.knowledge_base:
                texts = [item['text'] for item in self.knowledge_base]
                self.knowledge_vectors = self.vectorizer.fit_transform(texts)
                print(f"✅ Knowledge base built with {len(self.knowledge_base)} entries")
            else:
                print("⚠️ Knowledge base is empty")
                
        except Exception as e:
            print(f"Error building knowledge base: {e}")
            # Fallback to empty knowledge base
            self.knowledge_base = []
            self.knowledge_vectors = None
    
    def _create_herb_text(self, herb):
        """Create text representation for herb"""
        return f"""
        Herb: {herb.get('herb_name_english', '')} ({herb.get('herb_name_sanskrit', '')})
        Scientific Name: {herb.get('scientific_name', '')}
        Taste (Rasa): {herb.get('rasa', '')}
        Energy (Virya): {herb.get('virya', '')}
        Post-digestive effect (Vipaka): {herb.get('vipaka', '')}
        Special effect (Prabhava): {herb.get('prabhava', '')}
        Vata Effect: {herb.get('vata_effect', '')}
        Pitta Effect: {herb.get('pitta_effect', '')}
        Kapha Effect: {herb.get('kapha_effect', '')}
        Part Used: {herb.get('part_used', '')}
        Preparation Method: {herb.get('preparation_method', '')}
        Dosage: {herb.get('dosage', '')}
        Contraindications: {herb.get('contraindications', '')}
        Description: {herb.get('description', '')}
        """
    
    def _create_symptom_text(self, symptom):
        """Create text representation for symptom"""
        return f"""
        Symptom: {symptom.get('symptom_name', '')}
        Category: {symptom.get('symptom_category', '')}
        Associated Dosha: {symptom.get('associated_dosha', '')}
        Body System: {symptom.get('body_system', '')}
        Description: {symptom.get('description', '')}
        """
    
    def _create_prakriti_text(self, profile):
        """Create text representation for prakriti profile"""
        return f"""
        Prakriti Type: {profile.get('constitution_type', '')}
        Dominant Dosha: {profile.get('dominant_dosha', '')}
        Characteristics: {profile.get('characteristics', '')}
        Common Ailments: {profile.get('common_ailments', '')}
        Recommended Lifestyle: {profile.get('recommended_lifestyle', '')}
        """
    
    def _create_relationship_text(self, rel):
        """Create text representation for herb-symptom relationship"""
        return f"""
        Herb: {rel.get('herb_name', '')}
        Symptom: {rel.get('symptom_name', '')}
        Effectiveness Score: {rel.get('effectiveness_score', 0)}
        Classical Reference: {rel.get('classical_reference', '')}
        Dosage for Symptom: {rel.get('dosage_for_symptom', '')}
        Preparation Method: {rel.get('preparation_method', '')}
        Duration of Treatment: {rel.get('duration_of_treatment', '')}
        """
    
    def _preprocess_query(self, query):
        """Preprocess user query for better matching"""
        # Convert to lowercase
        query = query.lower()
        
        # Remove extra whitespace
        query = re.sub(r'\s+', ' ', query).strip()
        
        return query
    
    def _find_relevant_knowledge(self, query, top_k=3):
        """Find relevant knowledge using TF-IDF and cosine similarity"""
        if not self.knowledge_base or self.knowledge_vectors is None:
            return []
        
        # Preprocess query
        processed_query = self._preprocess_query(query)
        
        # Vectorize query
        query_vector = self.vectorizer.transform([processed_query])
        
        # Calculate cosine similarities
        similarities = cosine_similarity(query_vector, self.knowledge_vectors).flatten()
        
        # Get top-k most similar entries
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        # Filter out low similarity results
        relevant_knowledge = []
        for idx in top_indices:
            if similarities[idx] > 0.1:  # Threshold for relevance
                relevant_knowledge.append({
                    'knowledge': self.knowledge_base[idx],
                    'similarity': similarities[idx]
                })
        
        return relevant_knowledge
    
    def _generate_rag_response(self, query, relevant_knowledge):
        """Generate response using retrieved knowledge"""
        if not relevant_knowledge:
            return "I don't have specific information about that. You might want to consult with an Ayurvedic practitioner for personalized advice."
        
        response_parts = []
        
        # Sort by similarity
        relevant_knowledge.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Generate response based on knowledge type
        herbs_mentioned = []
        symptoms_mentioned = []
        prakriti_types = []
        
        for item in relevant_knowledge:
            knowledge = item['knowledge']
            similarity = item['similarity']
            
            if knowledge['type'] == 'herb':
                herb_info = f"""
                <div class="herb-info bg-green-50 p-4 rounded-lg mb-3">
                    <h4 class="font-bold text-green-800">{knowledge['name']} ({knowledge['sanskrit_name']})</h4>
                    <p><strong>Scientific Name:</strong> {knowledge['scientific_name']}</p>
                    <p><strong>Description:</strong> {knowledge['description']}</p>
                    <p><strong>Taste:</strong> {knowledge['rasa']} | <strong>Energy:</strong> {knowledge['virya']}</p>
                    <p><strong>Dosage:</strong> {knowledge['dosage']}</p>
                    <p><strong>Preparation:</strong> {knowledge['preparation_method']}</p>
                    {f'<p><strong>Contraindications:</strong> {knowledge["contraindications"]}</p>' if knowledge['contraindications'] else ''}
                </div>
                """
                response_parts.append(herb_info)
                herbs_mentioned.append(knowledge['name'])
                
            elif knowledge['type'] == 'symptom':
                symptom_info = f"""
                <div class="symptom-info bg-blue-50 p-4 rounded-lg mb-3">
                    <h4 class="font-bold text-blue-800">{knowledge['name']}</h4>
                    <p><strong>Category:</strong> {knowledge['category']}</p>
                    <p><strong>Associated Dosha:</strong> {knowledge['associated_dosha']}</p>
                    <p><strong>Description:</strong> {knowledge['description']}</p>
                </div>
                """
                response_parts.append(symptom_info)
                symptoms_mentioned.append(knowledge['name'])
                
            elif knowledge['type'] == 'prakriti':
                prakriti_info = f"""
                <div class="prakriti-info bg-purple-50 p-4 rounded-lg mb-3">
                    <h4 class="font-bold text-purple-800">{knowledge['constitution_type']}</h4>
                    <p><strong>Dominant Dosha:</strong> {knowledge['dominant_dosha']}</p>
                    <p><strong>Characteristics:</strong> {knowledge['characteristics']}</p>
                    <p><strong>Common Ailments:</strong> {knowledge['common_ailments']}</p>
                    <p><strong>Recommended Lifestyle:</strong> {knowledge['recommended_lifestyle']}</p>
                </div>
                """
                response_parts.append(prakriti_info)
                prakriti_types.append(knowledge['constitution_type'])
                
            elif knowledge['type'] == 'relationship':
                relationship_info = f"""
                <div class="relationship-info bg-yellow-50 p-4 rounded-lg mb-3">
                    <h4 class="font-bold text-yellow-800">{knowledge['herb_name']} for {knowledge['symptom_name']}</h4>
                    <p><strong>Effectiveness:</strong> {knowledge['effectiveness_score']}/1.00</p>
                    <p><strong>Dosage:</strong> {knowledge['dosage_for_symptom']}</p>
                    <p><strong>Preparation:</strong> {knowledge['preparation_method']}</p>
                    <p><strong>Treatment Duration:</strong> {knowledge['duration_of_treatment']}</p>
                </div>
                """
                response_parts.append(relationship_info)
        
        # Create a comprehensive response
        response = "<p>Based on your query, here's what I found:</p>"
        
        if response_parts:
            response += "".join(response_parts)
        
        # Add recommendations if relevant
        if herbs_mentioned and symptoms_mentioned:
            response += f"<p class='mt-3'><strong>Recommendation:</strong> Based on the symptoms you mentioned, {', '.join(herbs_mentioned)} might be helpful. However, please consult with an Ayurvedic practitioner for personalized advice.</p>"
        elif herbs_mentioned:
            response += f"<p class='mt-3'><strong>Note:</strong> {', '.join(herbs_mentioned)} has the properties mentioned above. Please consult with an Ayurvedic practitioner for proper dosage and personalized advice.</p>"
        
        return response
    
    def get_response(self, query):
        """Get RAG response for user query"""
        try:
            # Find relevant knowledge
            relevant_knowledge = self._find_relevant_knowledge(query, top_k=5)
            
            # Generate response using retrieved knowledge
            response = self._generate_rag_response(query, relevant_knowledge)
            
            return response
            
        except Exception as e:
            print(f"Error generating RAG response: {e}")
            return "I'm sorry, I encountered an error while processing your request. Please try again."

# Initialize the RAG chatbot service
rag_chatbot_service = RAGChatbotService()

def get_rag_chatbot_response(query):
    """Get RAG chatbot response for a query"""
    return rag_chatbot_service.get_response(query)