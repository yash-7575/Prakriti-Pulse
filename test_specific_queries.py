#!/usr/bin/env python3
"""
Test specific chatbot queries to verify direct answers
"""

import sys
import os

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import get_chatbot_response

def test_direct_answers():
    """Test that chatbot provides direct answers, not just links"""
    test_cases = [
        ("vata", "Should explain Vata dosha directly"),
        ("pitta", "Should explain Pitta dosha directly"),
        ("kapha", "Should explain Kapha dosha directly"),
        ("prakriti", "Should explain Prakriti concept directly"),
        ("ashwagandha", "Should explain Ashwagandha herb directly"),
        ("tulsi", "Should explain Tulsi herb directly"),
        ("triphala", "Should explain Triphala herb directly")
    ]
    
    print("Testing Direct Answers from Chatbot")
    print("=" * 50)
    
    for i, (query, description) in enumerate(test_cases, 1):
        print(f"\nTest {i}: {description}")
        print(f"Query: '{query}'")
        response = get_chatbot_response(query)
        
        # Check if response contains actual information (not just links)
        if "href=" in response:
            print("❌ Response contains links - not direct enough")
        else:
            print("✅ Response provides direct information")
            
        print(f"Response: {response[:200]}{'...' if len(response) > 200 else ''}")
        print("-" * 30)

if __name__ == "__main__":
    test_direct_answers()