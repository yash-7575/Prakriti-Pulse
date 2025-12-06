
import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

from chatbot_service import RAGChatbotService

def test_personalization():
    print("Initializing Chatbot Service...")
    chatbot = RAGChatbotService()
    
    # Test Case 1: Pitta Context
    context_pitta = {
        'prakriti': 'Pitta (Single Pitta)',
        'symptoms': 'Acidity, Skin Rash'
    }
    query = "What herbs should I take?"
    
    print("\n--- Test Case 1: Pitta Context ---")
    print(f"Context: {context_pitta}")
    print(f"Query: {query}")
    response = chatbot.get_response(query, context=context_pitta)
    print(f"Response: {response[:300]}...")
    
    if "Pitta" in response or "cooling" in response.lower() or "Amla" in response or "Shatavari" in response:
        print("✅ Success: Response seems tailored to Pitta/Acidity.")
    else:
        print("⚠️ Warning: Response might not be personalized enough.")

    # Test Case 2: Kapha Context
    context_kapha = {
        'prakriti': 'Kapha (Single Kapha)',
        'symptoms': 'Congestion, Lethargy'
    }
    query = "What herbs should I take?"
    
    print("\n--- Test Case 2: Kapha Context ---")
    print(f"Context: {context_kapha}")
    print(f"Query: {query}")
    response = chatbot.get_response(query, context=context_kapha)
    print(f"Response: {response[:300]}...")
    
    if "Kapha" in response or "warming" in response.lower() or "Ginger" in response or "Tulsi" in response:
        print("✅ Success: Response seems tailored to Kapha/Congestion.")
    else:
        print("⚠️ Warning: Response might not be personalized enough.")

    # Test Case 3: Why question
    query_why = "Why did you choose these herbs?"
    print("\n--- Test Case 3: Explanation ---")
    print(f"Query: {query_why}")
    response = chatbot.get_response(query_why, context=context_kapha)
    print(f"Response: {response[:300]}...")
    
    if "because" in response.lower() or "due to" in response.lower() or "Kapha" in response:
         print("✅ Success: Chatbot provided an explanation.")
    else:
         print("⚠️ Warning: Explanation might be missing.")

if __name__ == "__main__":
    test_personalization()
