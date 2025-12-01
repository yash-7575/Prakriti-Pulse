"""
Test script for RAG Chatbot Service
"""
import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from chatbot_service import RAGChatbotService
    print("✅ RAG Chatbot Service imported successfully")
    
    # Initialize the service
    chatbot = RAGChatbotService()
    print(f"✅ Knowledge base built with {len(chatbot.knowledge_base)} entries")
    
    # Test queries
    test_queries = [
        "What are the benefits of Ashwagandha?",
        "I have a headache, what herbs can help?",
        "Tell me about Vata constitution",
        "What is Triphala used for?",
        "I have acidity, what should I take?"
    ]
    
    print("\n🧪 Testing RAG responses:")
    for query in test_queries:
        print(f"\n❓ Query: {query}")
        response = chatbot.get_response(query)
        print(f"🤖 Response: {response[:200]}..." if len(response) > 200 else f"🤖 Response: {response}")
        
except ImportError as e:
    print(f"❌ Failed to import RAG Chatbot Service: {e}")
    print("Please install required packages:")
    print("pip install scikit-learn numpy scipy")
    
except Exception as e:
    print(f"❌ Error testing RAG Chatbot Service: {e}")
    import traceback
    traceback.print_exc()