
import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

from chatbot_service import rag_chatbot_service
from app import get_chatbot_response

def test_queries():
    print("--- Testing 'Herbs and their benefits' ---")
    try:
        response = rag_chatbot_service.get_response("Herbs and their benefits")
        print(f"Response: {response}")
    except Exception as e:
        print(f"Error caught in test: {e}")

    print("\n--- Testing 'What helps with headaches' ---")
    try:
        # Test direct RAG response
        rag_response = rag_chatbot_service.get_response("What helps with headaches")
        print(f"RAG Response: {rag_response}")
        
        # Test app-level response (which includes rule-based logic)
        app_response = get_chatbot_response("What helps with headaches")
        print(f"App Response: {app_response}")
    except Exception as e:
        print(f"Error caught in test: {e}")

if __name__ == "__main__":
    test_queries()
