from app import _get_rule_based_response

def test_response():
    query = "How to reduce acidity naturally"
    response = _get_rule_based_response(query.lower())
    print(f"Query: {query}")
    print(f"Response: {response}")
    
    if "I can help you understand symptoms" in response:
        print("FAIL: Got generic response instead of specific advice.")
    else:
        print("SUCCESS: Got specific response.")

if __name__ == "__main__":
    test_response()
