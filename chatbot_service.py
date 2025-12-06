"""
RAG Chatbot Service for Prakriti Pulse
Implements Retrieval-Augmented Generation for Ayurvedic herb recommendations
"""
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import os
import pandas as pd
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()
# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_AVAILABLE = False

if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        GEMINI_AVAILABLE = True
        print("Gemini API configured successfully")
    except Exception as e:
        print(f"Error configuring Gemini API: {e}")

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
        self.gemini_model = None
        
        if GEMINI_AVAILABLE:
            self.gemini_model = genai.GenerativeModel('gemini-2.5-flash')
            
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
        """Build knowledge base from database, mock data, and custom files"""
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
            
            # Process custom data file
            try:
                if os.path.exists('rag_data.txt'):
                    with open('rag_data.txt', 'r', encoding='utf-8') as f:
                        content = f.read()
                        # Split by double newlines to create chunks
                        chunks = [chunk.strip() for chunk in content.split('\n\n') if chunk.strip()]
                        for i, chunk in enumerate(chunks):
                            entry = {
                                'type': 'custom',
                                'id': f'custom_{i}',
                                'text': chunk
                            }
                            self.knowledge_base.append(entry)
                    print(f"Loaded {len(chunks)} custom data entries")
            except Exception as e:
                print(f"Error loading custom data: {e}")

            # Load GNN Dataset
            self._load_gnn_dataset()

            # Vectorize the knowledge base
            if self.knowledge_base:
                texts = [item['text'] for item in self.knowledge_base]
                
                # Use Gemini embeddings if available, otherwise TF-IDF
                if GEMINI_AVAILABLE:
                    try:
                        # Batch processing for embeddings to avoid rate limits
                        self.knowledge_vectors = []
                        batch_size = 10
                        for i in range(0, len(texts), batch_size):
                            batch = texts[i:i+batch_size]
                            embeddings = [genai.embed_content(
                                model="models/embedding-001",
                                content=text,
                                task_type="retrieval_document"
                            )['embedding'] for text in batch]
                            self.knowledge_vectors.extend(embeddings)
                        self.knowledge_vectors = np.array(self.knowledge_vectors)
                        print("Generated Gemini embeddings")
                    except Exception as e:
                        print(f"Error generating Gemini embeddings: {e}")
                        print("Fallback to TF-IDF")
                        self.knowledge_vectors = self.vectorizer.fit_transform(texts)
                else:
                    self.knowledge_vectors = self.vectorizer.fit_transform(texts)
                
                print(f"Knowledge base built with {len(self.knowledge_base)} entries")
            else:
                print("Knowledge base is empty")
                
        except Exception as e:
            import traceback
            print(f"Error building knowledge base: {e}")
            print(traceback.format_exc())
            # Fallback to empty knowledge base
            self.knowledge_base = []
            self.knowledge_vectors = None

    def _load_gnn_dataset(self):
        """Load data from the Ayurveda GNN dataset"""
        dataset_path = os.path.join(os.path.dirname(__file__), 'ayurveda_gnn_dataset_testing3', 'ayurveda_gnn_dataset')
        
        if not os.path.exists(dataset_path):
            print(f"GNN Dataset not found at {dataset_path}")
            return

        try:
            print("Loading GNN Dataset...")
            
            # Load Herbs
            herbs_path = os.path.join(dataset_path, 'nodes', 'herbs.csv')
            if os.path.exists(herbs_path):
                try:
                    df_herbs = pd.read_csv(herbs_path, on_bad_lines='skip', engine='python')
                except Exception as e:
                    print(f"Error reading herbs.csv: {e}")
                    df_herbs = pd.DataFrame()
                
                for _, row in df_herbs.iterrows():
                    text = f"""
                    Herb: {row.get('name', '')}
                    Scientific Name: {row.get('scientificname', '')}
                    Taste: {row.get('taste', '')}
                    Energy: {row.get('energy', '')}
                    Post-digestive effect: {row.get('postdigestiveeffect', '')}
                    Properties: {row.get('properties', '')}
                    Uses: {row.get('uses', '')}
                    Contraindications: {row.get('contraindications', '')}
                    """
                    entry = {
                        'type': 'herb',
                        'id': f"gnn_herb_{row.get('nodeid', '')}",
                        'name': row.get('name', ''),
                        'sanskrit_name': row.get('name', ''), # Assuming name is Sanskrit/Common
                        'scientific_name': row.get('scientificname', ''),
                        'rasa': row.get('taste', ''),
                        'virya': row.get('energy', ''),
                        'vipaka': row.get('postdigestiveeffect', ''),
                        'description': str(row.get('properties', '')) + " " + str(row.get('uses', '')),
                        'contraindications': row.get('contraindications', ''),
                        'text': text
                    }
                    self.knowledge_base.append(entry)
                print(f"Loaded {len(df_herbs)} herbs from GNN dataset")

            # Load Health Conditions
            conditions_path = os.path.join(dataset_path, 'nodes', 'health_conditions.csv')
            if os.path.exists(conditions_path):
                try:
                    df_conditions = pd.read_csv(conditions_path, on_bad_lines='skip', engine='python')
                except Exception as e:
                    print(f"Error reading health_conditions.csv: {e}")
                    df_conditions = pd.DataFrame()

                for _, row in df_conditions.iterrows():
                    text = f"""
                    Condition: {row.get('name', '')}
                    Description: {row.get('description', '')}
                    Dosha Imbalance: {row.get('primarydoshaimbalance', '')} (Primary), {row.get('secondarydoshaimbalance', '')} (Secondary)
                    Affected Systems: {row.get('affectedbodysystems', '')}
                    Severity: {row.get('severitylevel', '')}
                    """
                    entry = {
                        'type': 'condition',
                        'id': f"gnn_condition_{row.get('nodeid', '')}",
                        'name': row.get('name', ''),
                        'description': row.get('description', ''),
                        'dosha_imbalance': f"{row.get('primarydoshaimbalance', '')}, {row.get('secondarydoshaimbalance', '')}",
                        'text': text
                    }
                    self.knowledge_base.append(entry)
                print(f"Loaded {len(df_conditions)} conditions from GNN dataset")

            # Load Herb-Condition Relationships
            edges_path = os.path.join(dataset_path, 'edges', 'herb_treats_condition.csv')
            if os.path.exists(edges_path):
                try:
                    df_edges = pd.read_csv(edges_path, on_bad_lines='skip', engine='python')
                except Exception as e:
                    print(f"Error reading herb_treats_condition.csv: {e}")
                    df_edges = pd.DataFrame()

                for _, row in df_edges.iterrows():
                    text = f"""
                    Relationship: Herb treats Condition
                    Herb ID: {row.get('from_nodeid', '')}
                    Condition ID: {row.get('to_nodeid', '')}
                    """
                    entry = {
                        'type': 'relationship',
                        'herb_id': row.get('from_nodeid', ''),
                        'condition_id': row.get('to_nodeid', ''),
                        'text': text
                    }
                    self.knowledge_base.append(entry)
                print(f"Loaded {len(df_edges)} relationships from GNN dataset")

        except Exception as e:
            print(f"Error loading GNN dataset: {e}")
            import traceback
            print(traceback.format_exc())

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
        """Find relevant knowledge using Gemini embeddings or TF-IDF"""
        if not self.knowledge_base or self.knowledge_vectors is None:
            return []
        
        # Preprocess query
        processed_query = self._preprocess_query(query)
        
        try:
            if GEMINI_AVAILABLE and isinstance(self.knowledge_vectors, np.ndarray):
                # Use Gemini embeddings
                query_embedding = genai.embed_content(
                    model="models/embedding-001",
                    content=processed_query,
                    task_type="retrieval_query"
                )['embedding']
                
                # Calculate cosine similarities
                # Reshape query_embedding to (1, -1)
                query_vector = np.array(query_embedding).reshape(1, -1)
                similarities = cosine_similarity(query_vector, self.knowledge_vectors).flatten()
            else:
                # Use TF-IDF
                query_vector = self.vectorizer.transform([processed_query])
                similarities = cosine_similarity(query_vector, self.knowledge_vectors).flatten()
            
            # Get top-k most similar entries
            top_indices = np.argsort(similarities)[::-1][:top_k]

            # Filter out low similarity results
            relevant_knowledge = []
            for idx in top_indices:
                if similarities[idx] > 0.1:  # Threshold for relevance
                    relevant_knowledge.append({
                        'knowledge': self.knowledge_base[idx],
                        'similarity': float(similarities[idx])
                    })
            
            return relevant_knowledge
            
        except Exception as e:
            print(f"Error finding relevant knowledge: {e}")
            return []
    
    def _generate_rag_response(self, query, relevant_knowledge, context=None):
        """Generate response using retrieved knowledge and Gemini"""
        
        # Prepare user context string
        user_context_str = ""
        if context:
            if context.get('prakriti'):
                user_context_str += f"User Prakriti: {context['prakriti']}\n"
            if context.get('symptoms'):
                user_context_str += f"User Symptoms: {context['symptoms']}\n"
        
        if not relevant_knowledge:
            if GEMINI_AVAILABLE:
                # If no specific knowledge found, let Gemini answer with general knowledge but with a disclaimer
                try:
                    prompt = f"""
                    You are an Ayurvedic expert assistant for Prakriti Pulse.
                    User Query: {query}
                    {user_context_str}
                    
                    Please answer the query based on general Ayurvedic principles. 
                    Disclaimer: Mention that this is general information and they should consult a practitioner.
                    """
                    response = self.gemini_model.generate_content(prompt)
                    return response.text
                except Exception as e:
                    return "I don't have specific information about that. You might want to consult with an Ayurvedic practitioner for personalized advice."
            return "I don't have specific information about that. You might want to consult with an Ayurvedic practitioner for personalized advice."
        
        # Prepare context from relevant knowledge
        context_parts = []
        for item in relevant_knowledge:
            knowledge = item['knowledge']
            context_parts.append(f"--- Info (Type: {knowledge.get('type', 'General')}) ---\n{knowledge['text']}")
        
        knowledge_context = "\n\n".join(context_parts)
        
        if GEMINI_AVAILABLE:
            try:
                # Construct prompt carefully to avoid syntax errors
                prompt = "You are an Ayurvedic expert assistant for Prakriti Pulse.\n"
                prompt += "Use the following context to answer the user's question.\n\n"
                
                if user_context_str:
                    prompt += f"USER CONTEXT:\n{user_context_str}\n"
                    prompt += "IMPORTANT: Tailor your answer to the user's Prakriti and symptoms if relevant.\n\n"
                
                prompt += f"KNOWLEDGE CONTEXT:\n{knowledge_context}\n\n"
                prompt += f"User Query: {query}\n\n"
                prompt += "Instructions:\n"
                prompt += "1. Answer the query using ONLY the provided context if possible.\n"
                prompt += "2. If the context doesn't fully answer it, you can use your general knowledge but prioritize the context.\n"
                prompt += "3. Format the response with HTML tags (<b>, <ul>, <li>, <p>).\n"
                prompt += "4. STRICTLY use bullet points (<ul><li>) for the entire answer. Do not use paragraphs.\n"
                prompt += "5. Keep each bullet point SHORT (max 2 sentences).\n"
                prompt += "6. Do NOT include introductory or concluding fluff (e.g., 'Here are the recommendations...'). Start directly with the points.\n"
                prompt += "7. Explain 'Why' briefly within the bullet points.\n"
                prompt += "8. Mention confidence level and alternatives briefly as bullet points.\n"
                prompt += "9. If recommending herbs, mention contraindications if available.\n"
                prompt += "10. Be helpful but extremely CONCISE.\n"
                
                response = self.gemini_model.generate_content(prompt)
                return response.text
            except Exception as e:
                print(f"Gemini generation error: {e}")
                # Fallback to manual response generation
        
        # Fallback manual response generation (existing logic)
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
            
            try:
                if knowledge.get('type') == 'custom':
                     response_parts.append(f"<div class='custom-info bg-gray-50 p-4 rounded-lg mb-3'><p>{knowledge.get('text', '')}</p></div>")
                
                elif knowledge.get('type') == 'herb':
                    herb_info = f"""
                    <div class="herb-info bg-green-50 p-4 rounded-lg mb-3">
                        <h4 class="font-bold text-green-800">{knowledge.get('name', 'Unknown Herb')} ({knowledge.get('sanskrit_name', '')})</h4>
                        <p><strong>Scientific Name:</strong> {knowledge.get('scientific_name', '')}</p>
                        <p><strong>Description:</strong> {knowledge.get('description', '')}</p>
                        <p><strong>Taste:</strong> {knowledge.get('rasa', '')} | <strong>Energy:</strong> {knowledge.get('virya', '')}</p>
                        <p><strong>Dosage:</strong> {knowledge.get('dosage', '')}</p>
                        <p><strong>Preparation:</strong> {knowledge.get('preparation_method', '')}</p>
                        {f'<p><strong>Contraindications:</strong> {knowledge.get("contraindications", "")}</p>' if knowledge.get('contraindications') else ''}
                    </div>
                    """
                    response_parts.append(herb_info)
                    if knowledge.get('name'):
                        herbs_mentioned.append(knowledge['name'])
                    
                elif knowledge.get('type') == 'symptom':
                    symptom_info = f"""
                    <div class="symptom-info bg-blue-50 p-4 rounded-lg mb-3">
                        <h4 class="font-bold text-blue-800">{knowledge.get('name', 'Unknown Symptom')}</h4>
                        <p><strong>Category:</strong> {knowledge.get('category', '')}</p>
                        <p><strong>Associated Dosha:</strong> {knowledge.get('associated_dosha', '')}</p>
                        <p><strong>Description:</strong> {knowledge.get('description', '')}</p>
                    </div>
                    """
                    response_parts.append(symptom_info)
                    if knowledge.get('name'):
                        symptoms_mentioned.append(knowledge['name'])
                    
                elif knowledge.get('type') == 'prakriti':
                    prakriti_info = f"""
                    <div class="prakriti-info bg-purple-50 p-4 rounded-lg mb-3">
                        <h4 class="font-bold text-purple-800">{knowledge.get('constitution_type', 'Unknown Type')}</h4>
                        <p><strong>Dominant Dosha:</strong> {knowledge.get('dominant_dosha', '')}</p>
                        <p><strong>Characteristics:</strong> {knowledge.get('characteristics', '')}</p>
                        <p><strong>Common Ailments:</strong> {knowledge.get('common_ailments', '')}</p>
                        <p><strong>Recommended Lifestyle:</strong> {knowledge.get('recommended_lifestyle', '')}</p>
                    </div>
                    """
                    response_parts.append(prakriti_info)
                    if knowledge.get('constitution_type'):
                        prakriti_types.append(knowledge['constitution_type'])
                    
                elif knowledge.get('type') == 'relationship':
                    relationship_info = f"""
                    <div class="relationship-info bg-yellow-50 p-4 rounded-lg mb-3">
                        <h4 class="font-bold text-yellow-800">{knowledge.get('herb_name', '')} for {knowledge.get('symptom_name', '')}</h4>
                        <p><strong>Effectiveness:</strong> {knowledge.get('effectiveness_score', 0)}/1.00</p>
                        <p><strong>Dosage:</strong> {knowledge.get('dosage_for_symptom', '')}</p>
                        <p><strong>Preparation:</strong> {knowledge.get('preparation_method', '')}</p>
                        <p><strong>Treatment Duration:</strong> {knowledge.get('duration_of_treatment', '')}</p>
                    </div>
                    """
                    response_parts.append(relationship_info)
            except Exception as item_error:
                print(f"Error processing knowledge item: {item_error}")
                continue
        
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
    
    def get_response(self, query, context=None):
        """Get RAG response for user query"""
        try:
            # Find relevant knowledge
            relevant_knowledge = self._find_relevant_knowledge(query, top_k=5)
            
            # Generate response using retrieved knowledge
            response = self._generate_rag_response(query, relevant_knowledge, context)
            
            return response
            
        except Exception as e:
            print(f"Error generating RAG response: {e}")
            return "I'm sorry, I encountered an error while processing your request. Please try again."

# Initialize the RAG chatbot service
rag_chatbot_service = RAGChatbotService()

def get_rag_chatbot_response(query, context=None):
    """Get RAG chatbot response for a query"""
    return rag_chatbot_service.get_response(query, context)
