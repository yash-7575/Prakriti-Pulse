import pickle
import sys
import os

try:
    with open("ai_engine/mappings.pkl", "rb") as f:
        data = pickle.load(f)
    print("Pickle loaded successfully")
except Exception as e:
    print(f"Error loading pickle: {e}")
