#!/usr/bin/env python3
"""
Test script to verify database connectivity and basic functionality
"""

from database_config import (
    test_connection, get_herbs, get_symptoms, get_prakriti_profiles,
    get_herb_symptom_relationships, add_patient_profile
)

def test_database_connection():
    """Test basic database connection"""
    print("Testing database connection...")
    if test_connection():
        print("✅ Database connection successful!")
        return True
    else:
        print("❌ Database connection failed!")
        return False

def test_data_retrieval():
    """Test data retrieval functions"""
    print("\nTesting data retrieval...")
    
    try:
        # Test herbs retrieval
        herbs = get_herbs()
        print(f"✅ Retrieved {len(herbs)} herbs")
        
        # Test symptoms retrieval
        symptoms = get_symptoms()
        print(f"✅ Retrieved {len(symptoms)} symptoms")
        
        # Test prakriti profiles retrieval
        profiles = get_prakriti_profiles()
        print(f"✅ Retrieved {len(profiles)} prakriti profiles")
        
        # Test herb-symptom relationships
        relationships = get_herb_symptom_relationships()
        print(f"✅ Retrieved {len(relationships)} herb-symptom relationships")
        
        return True
        
    except Exception as e:
        print(f"❌ Data retrieval failed: {e}")
        return False

def test_patient_profile_creation():
    """Test patient profile creation"""
    print("\nTesting patient profile creation...")
    
    try:
        result = add_patient_profile(
            age=30,
            gender='Male',
            prakriti_type='Vata',
            current_symptoms='Headache, Fatigue',
            symptom_severity='Moderate',
            treatment_history='None',
            effectiveness_rating=0.0,
            practitioner_notes='Test patient profile'
        )
        
        if result:
            print("✅ Patient profile created successfully!")
            return True
        else:
            print("❌ Patient profile creation failed!")
            return False
            
    except Exception as e:
        print(f"❌ Patient profile creation failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Starting Prakriti Pulse Database Tests\n")
    
    # Test database connection
    if not test_database_connection():
        print("\n❌ Database connection test failed. Please check your database configuration.")
        return False
    
    # Test data retrieval
    if not test_data_retrieval():
        print("\n❌ Data retrieval test failed.")
        return False
    
    # Test patient profile creation
    if not test_patient_profile_creation():
        print("\n❌ Patient profile creation test failed.")
        return False
    
    print("\n🎉 All tests passed! Database is ready for use.")
    return True

if __name__ == "__main__":
    main()
