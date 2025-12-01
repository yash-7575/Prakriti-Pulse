#!/usr/bin/env python3
"""
Test script for the Prakriti Pulse chatbot
"""

import sys
import os

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import get_chatbot_response

def test_chatbot():
    """Test the chatbot with various inputs"""
    test_cases = [
        "hello",
        "what is prakriti",
        "tell me about vata",
        "what helps with headaches",
        "benefits of ashwagandha",
        "how to balance pitta",
        "what is triphala",
        "help"
    ]
    
    print("Testing Prakriti Pulse Chatbot")
    print("=" * 40)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: '{test_case}'")
        response = get_chatbot_response(test_case)
        print(f"Response: {response}")
        print("-" * 30)

if __name__ == "__main__":
    test_chatbot()