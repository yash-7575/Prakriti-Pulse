from chatbot_service import rag_chatbot_service
import traceback

def test_gnn_loading():
    try:
        print(f"Knowledge Base Size: {len(rag_chatbot_service.knowledge_base)}")
        
        # Check for GNN entries
        gnn_herbs = [e for e in rag_chatbot_service.knowledge_base if str(e.get('id', '')).startswith('gnn_herb')]
        gnn_conditions = [e for e in rag_chatbot_service.knowledge_base if str(e.get('id', '')).startswith('gnn_condition')]
        
        print(f"GNN Herbs Loaded: {len(gnn_herbs)}")
        print(f"GNN Conditions Loaded: {len(gnn_conditions)}")
        
        if gnn_herbs:
            print(f"Sample GNN Herb: {gnn_herbs[0]['name']}")
            
        if gnn_conditions:
            print(f"Sample GNN Condition: {gnn_conditions[0]['name']}")
    except Exception as e:
        print(f"Error building knowledge base: {e}")
        print(traceback.format_exc())

if __name__ == "__main__":
    test_gnn_loading()

