#!/usr/bin/env python3
"""
Database setup script for Prakriti Pulse
This script helps you set up the MySQL database with all tables and sample data
"""

import mysql.connector
from mysql.connector import Error
import os
import sys

def create_database_connection():
    """Create database connection"""
    try:
        # You can modify these connection parameters
        connection = mysql.connector.connect(
            host='localhost',
            user='root',  # Change to your MySQL username
            password='',  # Change to your MySQL password
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        
        if connection.is_connected():
            print("✅ Successfully connected to MySQL server")
            return connection
            
    except Error as e:
        print(f"❌ Error connecting to MySQL: {e}")
        return None

def execute_sql_file(connection, sql_file_path):
    """Execute SQL file"""
    try:
        cursor = connection.cursor()
        
        # Read the SQL file
        with open(sql_file_path, 'r', encoding='utf-8') as file:
            sql_content = file.read()
        
        # Split by semicolon and execute each statement
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        for statement in statements:
            if statement:
                cursor.execute(statement)
                print(f"✅ Executed: {statement[:50]}...")
        
        connection.commit()
        print("✅ Database setup completed successfully!")
        
    except Error as e:
        print(f"❌ Error executing SQL file: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
    
    return True

def test_database_connection():
    """Test connection to the created database"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',  # Change to your MySQL username
            password='',  # Change to your MySQL password
            database='Prakriti_Pulse',
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        
        if connection.is_connected():
            print("✅ Successfully connected to Prakriti_Pulse database")
            
            cursor = connection.cursor()
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            print(f"📊 Found {len(tables)} tables:")
            for table in tables:
                print(f"   - {table[0]}")
            
            # Test data counts
            cursor.execute("SELECT COUNT(*) FROM herbs")
            herb_count = cursor.fetchone()[0]
            print(f"🌿 Herbs: {herb_count} records")
            
            cursor.execute("SELECT COUNT(*) FROM symptoms")
            symptom_count = cursor.fetchone()[0]
            print(f"🔍 Symptoms: {symptom_count} records")
            
            cursor.execute("SELECT COUNT(*) FROM prakriti_profiles")
            profile_count = cursor.fetchone()[0]
            print(f"🧘 Prakriti Profiles: {profile_count} records")
            
            return True
            
    except Error as e:
        print(f"❌ Error testing database: {e}")
        return False
    finally:
        if connection and connection.is_connected():
            cursor.close()
            connection.close()

def main():
    """Main function"""
    print("🌿 Prakriti Pulse Database Setup")
    print("=" * 40)
    
    # Check if SQL file exists
    sql_file = "database_setup.sql"
    if not os.path.exists(sql_file):
        print(f"❌ SQL file '{sql_file}' not found!")
        print("Make sure 'database_setup.sql' is in the same directory as this script.")
        return
    
    # Create connection
    connection = create_database_connection()
    if not connection:
        return
    
    try:
        # Execute SQL file
        print(f"📄 Executing SQL file: {sql_file}")
        if execute_sql_file(connection, sql_file):
            print("\n🎉 Database setup completed!")
            
            # Test the database
            print("\n🧪 Testing database connection...")
            if test_database_connection():
                print("\n✅ Database is ready to use!")
                print("\nNext steps:")
                print("1. Update your Flask app configuration with database credentials")
                print("2. Install required Python packages: pip install mysql-connector-python")
                print("3. Start using the database in your Flask application")
            else:
                print("❌ Database test failed!")
        else:
            print("❌ Database setup failed!")
            
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        if connection and connection.is_connected():
            connection.close()
            print("🔌 Database connection closed")

if __name__ == "__main__":
    main()
