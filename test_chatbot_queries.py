
import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

from chatbot_service import RAGChatbotService

def test_chatbot_queries():
    print("Initializing Chatbot Service...")
    chatbot = RAGChatbotService()
    
    queries = [
        "Which herbs are commonly available in Kerala?",
        "I live in Maharashtra — suggest herbs suited for this climate.",
        "Which herbs grow naturally in Assam?",
        "What herbs are good for humid climates?",
        "Tell me about Ashwagandha availability."
    ]
    
    print("\n--- Starting Verification ---")
    
    for query in queries:
        print(f"\nQuery: {query}")
        response = chatbot.get_response(query)
        print(f"Response: {response[:200]}...") # Print first 200 chars
        
        # Basic validation
        if "I don't have specific information" in response:
            print("❌ Failed: Chatbot could not answer.")
        else:
            print("✅ Success: Chatbot provided an answer.")

if __name__ == "__main__":
    test_chatbot_queries()
