import os
import pandas as pd
from neo4j import GraphDatabase

# CONFIGURATION
# If using Neo4j Desktop, use "bolt://localhost:7687"
URI = "neo4j://127.0.0.1:7687"
AUTH = ("neo4j", "ayurveda_password") # Must match what you set in Desktop

class AyurvedaGraphLoader:
    def __init__(self):
        self.driver = GraphDatabase.driver(URI, auth=AUTH)

    def close(self):
        self.driver.close()

    def create_constraints(self):
        """Creates unique constraints to ensure data integrity."""
        print("🔒 Creating constraints for new schema...")
        # Added constraints for the NEW node types
        queries = [
            "CREATE CONSTRAINT IF NOT EXISTS FOR (h:Herb) REQUIRE h.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Condition) REQUIRE c.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (d:Dosha) REQUIRE d.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (s:Symptom) REQUIRE s.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (b:BodyPart) REQUIRE b.id IS UNIQUE",
            # NEW NODES
            "CREATE CONSTRAINT IF NOT EXISTS FOR (sr:Srota) REQUIRE sr.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (g:Guna) REQUIRE g.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (r:Rasa) REQUIRE r.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (cg:ChemicalGroup) REQUIRE cg.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (a:Action) REQUIRE a.id IS UNIQUE"
        ]
        with self.driver.session() as session:
            for q in queries:
                session.run(q)

    def load_nodes(self, folder_path):
        """Loads Node CSVs."""
        # UPDATED Mapping: Filename -> Label
        file_mapping = {
            'herbs.csv': 'Herb',
            'health_conditions.csv': 'Condition',
            'doshas.csv': 'Dosha',
            'symptoms.csv': 'Symptom',
            'body_parts.csv': 'BodyPart',
            # NEW FILES
            'srotas.csv': 'Srota',
            'guna.csv': 'Guna',
            'rasa.csv': 'Rasa',
            'chemical_groups.csv': 'ChemicalGroup',
            'actions.csv': 'Action'
        }
        
        with self.driver.session() as session:
            for filename, label in file_mapping.items():
                file_path = os.path.join(folder_path, filename)
                if os.path.exists(file_path):
                    print(f"📦 Loading Nodes: {label} from {filename}...")
                    df = pd.read_csv(file_path)
                    
                    query = f"""
                    UNWIND $rows AS row
                    MERGE (n:{label} {{id: toInteger(row.node_id)}})
                    SET n += row
                    """
                    session.run(query, rows=df.to_dict('records'))

    def load_edges(self, folder_path):
        """Loads Relationship CSVs."""
        # UPDATED Mapping
        edge_mapping = {
            # Original
            'herb_treats_condition.csv': ('Herb', 'Condition', 'TREATS'),
            'herb_balances_dosha.csv': ('Herb', 'Dosha', 'BALANCES'),
            'condition_aggravates_dosha.csv': ('Condition', 'Dosha', 'AGGRAVATES'),
            'condition_manifests_as_symptom.csv': ('Condition', 'Symptom', 'MANIFESTS_AS'),
            'herb_targets_body_part.csv': ('Herb', 'BodyPart', 'TARGETS'),
            'condition_affects_body_part.csv': ('Condition', 'BodyPart', 'AFFECTS'),
            'dosha_governs_body_part.csv': ('Dosha', 'BodyPart', 'GOVERNS'),
            'symptom_indicates_dosha_imbalance.csv': ('Symptom', 'Dosha', 'INDICATES'),
            
            # NEW EDGES
            'condition_affects_srotas.csv': ('Condition', 'Srota', 'AFFECTS_SROTA'),
            'herb_has_rasa.csv': ('Herb', 'Rasa', 'HAS_RASA'),
            'herb_has_guna.csv': ('Herb', 'Guna', 'HAS_GUNA'),
            'herb_has_chemical_group.csv': ('Herb', 'ChemicalGroup', 'CONTAINS_CHEMICAL'),
            'herb_has_action.csv': ('Herb', 'Action', 'EXHIBITS_ACTION')
        }

        with self.driver.session() as session:
            for filename, (src_lbl, tgt_lbl, rel_type) in edge_mapping.items():
                file_path = os.path.join(folder_path, filename)
                if os.path.exists(file_path):
                    print(f"🔗 Linking: {src_lbl} -[{rel_type}]-> {tgt_lbl}...")
                    df = pd.read_csv(file_path)
                    
                    query = f"""
                    UNWIND $rows AS row
                    MATCH (source:{src_lbl} {{id: toInteger(row.source_node_id)}})
                    MATCH (target:{tgt_lbl} {{id: toInteger(row.target_node_id)}})
                    MERGE (source)-[r:{rel_type}]->(target)
                    SET r += row
                    """
                    session.run(query, rows=df.to_dict('records'))

if __name__ == "__main__":
    # Ensure these paths match your folder structure
    NODES_PATH = "./nodes" 
    EDGES_PATH = "./edges"

    loader = AyurvedaGraphLoader()
    try:
        loader.create_constraints()
        loader.load_nodes(NODES_PATH)
        loader.load_edges(EDGES_PATH)
        print("🚀 Extended Knowledge Graph Built Successfully!")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        loader.close()