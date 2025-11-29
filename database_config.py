"""
Database configuration for Prakriti Pulse Flask application
"""

import mysql.connector
from mysql.connector import Error
import os
from flask import current_app

class DatabaseConfig:
    """Database configuration and connection management"""
    
    def __init__(self):
        self.host = os.environ.get('DB_HOST', 'localhost')
        self.user = os.environ.get('DB_USER', 'root')
        self.password = os.environ.get('DB_PASSWORD', '')
        self.database = os.environ.get('DB_NAME', 'Prakriti_Pulse')
        self.charset = 'utf8mb4'
        self.collation = 'utf8mb4_unicode_ci'
    
    def get_connection(self):
        """Get database connection"""
        try:
            connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                charset=self.charset,
                collation=self.collation,
                autocommit=True
            )
            
            if connection.is_connected():
                return connection
            else:
                return None
                
        except Error as e:
            print(f"Database connection error: {e}")
            return None
    
    def execute_query(self, query, params=None, fetch=False):
        """Execute a database query"""
        connection = None
        cursor = None
        
        try:
            connection = self.get_connection()
            if not connection:
                return None
            
            cursor = connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            
            if fetch:
                return cursor.fetchall()
            else:
                connection.commit()
                return cursor.rowcount
                
        except Error as e:
            print(f"Query execution error: {e}")
            return None
        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()

# Database helper functions
def get_herbs():
    """Get all herbs from database"""
    db = DatabaseConfig()
    query = "SELECT * FROM herbs ORDER BY herb_name_english"
    return db.execute_query(query, fetch=True)

def get_symptoms():
    """Get all symptoms from database"""
    db = DatabaseConfig()
    query = "SELECT * FROM symptoms ORDER BY symptom_name"
    return db.execute_query(query, fetch=True)

def get_prakriti_profiles():
    """Get all prakriti profiles from database"""
    db = DatabaseConfig()
    query = "SELECT * FROM prakriti_profiles ORDER BY profile_id"
    return db.execute_query(query, fetch=True)

def get_herb_symptom_relationships():
    """Get herb-symptom relationships"""
    db = DatabaseConfig()
    query = """
    SELECT hsr.*, h.herb_name_english, s.symptom_name 
    FROM herb_symptom_relationships hsr
    JOIN herbs h ON hsr.herb_id = h.herb_id
    JOIN symptoms s ON hsr.symptom_id = s.symptom_id
    ORDER BY hsr.effectiveness_score DESC
    """
    return db.execute_query(query, fetch=True)

def get_formulations():
    """Get all formulations from database"""
    db = DatabaseConfig()
    query = "SELECT * FROM formulations ORDER BY formulation_name"
    return db.execute_query(query, fetch=True)

def get_herbs_for_symptom(symptom_id):
    """Get herbs recommended for a specific symptom"""
    db = DatabaseConfig()
    query = """
    SELECT h.*, hsr.effectiveness_score, hsr.dosage_for_symptom, 
           hsr.preparation_method, hsr.duration_of_treatment
    FROM herbs h
    JOIN herb_symptom_relationships hsr ON h.herb_id = hsr.herb_id
    WHERE hsr.symptom_id = %s
    ORDER BY hsr.effectiveness_score DESC
    """
    return db.execute_query(query, (symptom_id,), fetch=True)

def get_symptoms_for_herb(herb_id):
    """Get symptoms that a specific herb can help with"""
    db = DatabaseConfig()
    query = """
    SELECT s.*, hsr.effectiveness_score, hsr.dosage_for_symptom,
           hsr.preparation_method, hsr.duration_of_treatment
    FROM symptoms s
    JOIN herb_symptom_relationships hsr ON s.symptom_id = hsr.symptom_id
    WHERE hsr.herb_id = %s
    ORDER BY hsr.effectiveness_score DESC
    """
    return db.execute_query(query, (herb_id,), fetch=True)

def get_prakriti_profile_by_scores(vata_score, pitta_score, kapha_score):
    """Get prakriti profile based on dosha scores"""
    db = DatabaseConfig()
    query = """
    SELECT * FROM prakriti_profiles 
    WHERE vata_score = %s AND pitta_score = %s AND kapha_score = %s
    LIMIT 1
    """
    return db.execute_query(query, (vata_score, pitta_score, kapha_score), fetch=True)

def add_patient_profile(age, gender, prakriti_type, current_symptoms, 
                       symptom_severity, treatment_history, effectiveness_rating, 
                       practitioner_notes):
    """Add a new patient profile"""
    db = DatabaseConfig()
    query = """
    INSERT INTO patient_profiles 
    (age, gender, prakriti_type, current_symptoms, symptom_severity, 
     treatment_history, effectiveness_rating, practitioner_notes)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    return db.execute_query(query, (age, gender, prakriti_type, current_symptoms,
                                   symptom_severity, treatment_history, 
                                   effectiveness_rating, practitioner_notes))

def get_patient_profiles():
    """Get all patient profiles"""
    db = DatabaseConfig()
    query = "SELECT * FROM patient_profiles ORDER BY patient_id DESC"
    return db.execute_query(query, fetch=True)

# Test database connection
def test_connection():
    """Test database connection"""
    db = DatabaseConfig()
    connection = db.get_connection()
    if connection:
        print("✅ Database connection successful!")
        connection.close()
        return True
    else:
        print("❌ Database connection failed!")
        return False
