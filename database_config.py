from neo4j import GraphDatabase
from datetime import datetime

class DatabaseConfig:
    def __init__(self):
        # Connect to the local Neo4j Database
        self.uri = "neo4j://localhost:7687"
        self.auth = ("neo4j", "ayurveda_password")
        self.driver = GraphDatabase.driver(self.uri, auth=self.auth)

    def close(self):
        self.driver.close()

    def get_herbs(self):
        """
        Return all nodes labeled :Herb.
        """
        query = """
        MATCH (h:Herb)
        RETURN h.herb_id as herb_id,
               h.name as herb_name_english,
               h.sanskrit_name as herb_name_sanskrit,
               h.scientific_name as scientific_name,
               h.rasa as rasa,
               h.virya as virya,
               h.vipaka as vipaka,
               h.prabhava as prabhava,
               h.vata_effect as vata_effect,
               h.pitta_effect as pitta_effect,
               h.kapha_effect as kapha_effect,
               h.part_used as part_used,
               h.dosage as dosage,
               h.preparation_method as preparation_method,
               h.contraindications as contraindications,
               h.description as description
        """
        with self.driver.session() as session:
            result = session.run(query)
            return [record.data() for record in result]

    def get_symptoms(self):
        """
        Return all nodes labeled :Symptom.
        """
        query = """
        MATCH (s:Symptom)
        RETURN s.symptom_id as symptom_id,
               s.name as symptom_name,
               s.category as symptom_category,
               s.description as description
        """
        with self.driver.session() as session:
            result = session.run(query)
            return [record.data() for record in result]

    def add_patient_profile(self, age, gender, prakriti_type, symptoms, severity, treatment_history, effectiveness, practitioner_notes):
        """
        Create a node (:Patient) and save these as properties.
        """
        query = """
        CREATE (p:Patient {
            age: $age,
            gender: $gender,
            prakriti_type: $prakriti_type,
            symptoms: $symptoms,
            severity: $severity,
            treatment_history: $treatment_history,
            effectiveness: $effectiveness,
            practitioner_notes: $practitioner_notes,
            created_at: $created_at
        })
        RETURN id(p) as patient_id
        """
        with self.driver.session() as session:
            result = session.run(query, 
                               age=age, 
                               gender=gender, 
                               prakriti_type=prakriti_type, 
                               symptoms=symptoms, 
                               severity=severity,
                               treatment_history=treatment_history,
                               effectiveness=effectiveness,
                               practitioner_notes=practitioner_notes,
                               created_at=datetime.now().isoformat())
            record = result.single()
            return record["patient_id"] if record else None

    def get_herbs_for_symptom(self, symptom_id):
        """
        Finds herbs connected to that symptom (or via a condition).
        Assuming symptom_id is passed, but if it's a name we might need to adjust.
        Based on app.py usage, it seems to be an ID or name from the form.
        Let's assume it matches the 'symptom_id' property or 'name' if passed as string.
        """
        query = """
        MATCH (s:Symptom) WHERE toString(s.symptom_id) = toString($symptom_id) OR s.name = $symptom_id
        MATCH (h:Herb)-[:TREATS]->(c:Condition)-[:MANIFESTS_AS]->(s)
        RETURN DISTINCT h.herb_id as herb_id,
                        h.name as herb_name_english,
                        h.sanskrit_name as herb_name_sanskrit,
                        h.scientific_name as scientific_name,
                        h.rasa as rasa,
                        h.virya as virya,
                        h.vipaka as vipaka,
                        h.prabhava as prabhava,
                        h.vata_effect as vata_effect,
                        h.pitta_effect as pitta_effect,
                        h.kapha_effect as kapha_effect,
                        h.part_used as part_used,
                        h.dosage as dosage,
                        h.preparation_method as preparation_method,
                        h.contraindications as contraindications,
                        h.description as description,
                        1.0 as effectiveness_score 
        """
        # Note: effectiveness_score is hardcoded for now as it wasn't in the original schema explicitly
        with self.driver.session() as session:
            result = session.run(query, symptom_id=symptom_id)
            return [record.data() for record in result]

    def get_symptoms_for_herb(self, herb_id):
        """
        Find symptoms treated by a specific herb.
        """
        query = """
        MATCH (h:Herb) WHERE toString(h.herb_id) = toString($herb_id)
        MATCH (h)-[:TREATS]->(c:Condition)-[:MANIFESTS_AS]->(s:Symptom)
        RETURN DISTINCT s.symptom_id as symptom_id,
                        s.name as symptom_name,
                        s.category as symptom_category,
                        s.description as description
        """
        with self.driver.session() as session:
            result = session.run(query, herb_id=herb_id)
            return [record.data() for record in result]

    def get_formulations(self):
        """
        Return all formulations.
        """
        query = """
        MATCH (f:Formulation)
        RETURN f.name as name, f.description as description
        """
        with self.driver.session() as session:
            result = session.run(query)
            return [record.data() for record in result]
            
    def get_prakriti_profile_by_scores(self, vata, pitta, kapha):
        """
        Determine prakriti profile based on scores.
        This is a placeholder logic or could be a DB lookup if you have profiles stored.
        """
        # Simple logic to determine dominant dosha
        scores = {'vata': vata, 'pitta': pitta, 'kapha': kapha}
        dominant = max(scores, key=scores.get)
        
        return [{
            'dominant_dosha': dominant,
            'constitution_type': f"{dominant.title()} Dominant",
            'characteristics': f"High {dominant} characteristics.",
            'common_ailments': "Varies based on imbalance.",
            'recommended_lifestyle': "Balance with opposite qualities."
        }]