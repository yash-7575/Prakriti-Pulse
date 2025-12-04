import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

try:
    from ai_engine.inference import AyurvedicAI

    print("Initializing AyurvedicAI...")
    ai = AyurvedicAI()
    print("Success: AI Engine initialized.")

    # Test inference
    symptom = "Insomnia"
    print(f"Testing inference for: {symptom}")
    recommendations = ai.get_recommendations(symptom)
    print("Recommendations:", recommendations)

except Exception as e:
    with open("error.log", "w") as f:
        import traceback

        traceback.print_exc(file=f)
    print(f"FAILED: {e}")
