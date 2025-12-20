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
        RETURN h.id as herb_id,
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
        RETURN s.id as symptom_id,
               s.name as symptom_name,
               s.category as symptom_category,
               s.description as description
        """
        with self.driver.session() as session:
            result = session.run(query)
            return [record.data() for record in result]

    def add_patient_profile(
        self,
        age,
        gender,
        state,
        prakriti_type,
        symptoms,
        severity,
        treatment_history,
        effectiveness,
        practitioner_notes,
    ):
        """
        Create a node (:Patient) and save these as properties.
        """
        query = """
        CREATE (p:Patient {
            age: $age,
            gender: $gender,
            state: $state,
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
            result = session.run(
                query,
                age=age,
                gender=gender,
                state=state,
                prakriti_type=prakriti_type,
                symptoms=symptoms,
                severity=severity,
                treatment_history=treatment_history,
                effectiveness=effectiveness,
                practitioner_notes=practitioner_notes,
                created_at=datetime.now().isoformat(),
            )
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
        MATCH (s:Symptom) WHERE toString(s.id) = toString($symptom_id) OR s.name = $symptom_id
        MATCH (h:Herb)-[:TREATS]->(c:Condition)-[:MANIFESTS_AS]->(s)
        RETURN DISTINCT h.id as herb_id,
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
        MATCH (h:Herb) WHERE toString(h.id) = toString($herb_id)
        MATCH (h)-[:TREATS]->(c:Condition)-[:MANIFESTS_AS]->(s:Symptom)
        RETURN DISTINCT s.id as symptom_id,
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
        scores = {"vata": vata, "pitta": pitta, "kapha": kapha}
        dominant = max(scores, key=scores.get)

        return [
            {
                "dominant_dosha": dominant,
                "constitution_type": f"{dominant.title()} Dominant",
                "characteristics": f"High {dominant} characteristics.",
                "common_ailments": "Varies based on imbalance.",
                "recommended_lifestyle": "Balance with opposite qualities.",
            }
        ]

    # graph based recommendations
    def get_graph_recommendations(self, symptom_ids):
        """
        Fetches herbs directly from the Graph DB based on symptom connections.
        """
        # Ensure IDs are integers for the query if they are numeric strings
        # The user query expects $symptom_ids
        try:
            # Try converting to int if they look like integers, otherwise keep as strings
            # depending on how they are stored in DB.
            # Based on previous code, they might be integers.
            # But the user didn't explicitly ask for conversion, just the query.
            # However, usually form data comes as strings.
            # I will convert to int to be safe as IDs are usually ints in this app's context
            # (seen in previous get_graph_recommendations implementation).
            symptom_ids = [int(x) for x in symptom_ids]
        except ValueError:
            # If conversion fails, pass as is (maybe they are string IDs)
            pass

        query = """
        MATCH (s:Symptom) WHERE s.id IN $symptom_ids
        MATCH (c:Condition)-[:MANIFESTS_AS]->(s)
        MATCH (h:Herb)-[r:TREATS]->(c)
        RETURN DISTINCT h.name as name, h.scientific_name as scientific_name, h.medicine_forms as form, c.name as reason, r.efficacy_score as score
        ORDER BY score DESC LIMIT 5
        """

        with self.driver.session() as session:
            result = session.run(query, symptom_ids=symptom_ids)
            data = [record.data() for record in result]

            # Post-process to format score as percentage
            for item in data:
                if "score" in item and item["score"] is not None:
                    # Assuming score is 0.0 to 1.0, convert to 0-100 int
                    item["score"] = int(item["score"] * 100)
                else:
                    item["score"] = 0

            return data
