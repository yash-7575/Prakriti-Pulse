# Prakriti Pulse Database Setup

This document explains how to set up the MySQL database for the Prakriti Pulse application.

## Database Schema

The database contains 6 main tables:

### 1. **herbs** - Ayurvedic herbs information
- `herb_id` (Primary Key)
- `herb_name_english`, `herb_name_sanskrit`, `herb_name_hindi`
- `rasa`, `virya`, `vipaka`, `prabhava` (Ayurvedic properties)
- `vata_effect`, `pitta_effect`, `kapha_effect` (Dosha effects)
- `part_used`, `preparation_method`, `dosage`, `contraindications`
- `scientific_name`, `description`

### 2. **symptoms** - Health symptoms
- `symptom_id` (Primary Key)
- `symptom_name`, `symptom_category`, `associated_dosha`
- `severity_level`, `body_system`, `description`, `synonyms`

### 3. **prakriti_profiles** - Ayurvedic constitution profiles
- `profile_id` (Primary Key)
- `vata_score`, `pitta_score`, `kapha_score`
- `dominant_dosha`, `constitution_type`
- `characteristics`, `common_ailments`, `recommended_lifestyle`

### 4. **herb_symptom_relationships** - Herb-symptom effectiveness mapping
- `relationship_id` (Primary Key)
- `herb_id` (Foreign Key to herbs)
- `symptom_id` (Foreign Key to symptoms)
- `effectiveness_score` (0.00-1.00 scale)
- `classical_reference`, `dosage_for_symptom`, `preparation_method`
- `duration_of_treatment`, `supporting_herbs`

### 5. **patient_profiles** - Patient treatment records
- `patient_id` (Primary Key)
- `age`, `gender`, `prakriti_type`
- `current_symptoms`, `symptom_severity`
- `treatment_history`, `effectiveness_rating`, `practitioner_notes`

### 6. **formulations** - Ayurvedic compound preparations
- `formulation_id` (Primary Key)
- `formulation_name`, `herb_ids`, `proportions`
- `indication`, `preparation_method`, `classical_reference`
- `modern_research`, `availability`

## Setup Instructions

### Method 1: Automated Setup (Recommended)

1. **Prerequisites:**
   - MySQL server running
   - Python installed
   - MySQL root access (or update credentials in scripts)

2. **Run the setup:**
   ```bash
   # On Windows
   setup_db.bat
   
   # On Linux/Mac
   python setup_database.py
   ```

### Method 2: Manual Setup

1. **Install MySQL connector:**
   ```bash
   pip install mysql-connector-python python-dotenv
   ```

2. **Run the SQL file:**
   ```bash
   mysql -u root -p < database_setup.sql
   ```

3. **Verify setup:**
   ```bash
   python -c "from database_config import test_connection; test_connection()"
   ```

## Configuration

### Environment Variables (Optional)

Create a `.env` file in the flask_app directory:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=Prakriti_Pulse
```

### Manual Configuration

Edit `database_config.py` to update connection parameters:

```python
def __init__(self):
    self.host = 'localhost'        # Your MySQL host
    self.user = 'root'             # Your MySQL username
    self.password = 'your_password' # Your MySQL password
    self.database = 'Prakriti_Pulse'
```

## Sample Data

The database comes pre-populated with:

- **10 Herbs**: Ashwagandha, Tulsi, Triphala, Brahmi, Neem, Amla, Shatavari, Guduchi, Haritaki, Arjuna
- **10 Symptoms**: Headache, Indigestion, Fatigue, Acidity, Joint Pain, Cough, Skin Rash, Fever, Constipation, Insomnia
- **10 Prakriti Profiles**: Various dosha combinations and characteristics
- **10 Herb-Symptom Relationships**: Effectiveness mappings with classical references
- **10 Patient Profiles**: Sample treatment records
- **10 Formulations**: Traditional Ayurvedic preparations

## Usage in Flask App

```python
from database_config import get_herbs, get_symptoms, get_herbs_for_symptom

# Get all herbs
herbs = get_herbs()

# Get all symptoms
symptoms = get_symptoms()

# Get herbs for a specific symptom
herbs_for_headache = get_herbs_for_symptom(1)  # symptom_id = 1 for headache
```

## Troubleshooting

### Common Issues:

1. **Connection Error:**
   - Check MySQL server is running
   - Verify username/password
   - Ensure database exists

2. **Permission Error:**
   - Grant proper privileges to MySQL user
   - Check firewall settings

3. **Character Encoding:**
   - Database uses UTF-8 encoding
   - Ensure MySQL supports Unicode

### Testing Connection:

```python
from database_config import test_connection
test_connection()
```

## Database Maintenance

### Backup:
```bash
mysqldump -u root -p Prakriti_Pulse > prakriti_backup.sql
```

### Restore:
```bash
mysql -u root -p Prakriti_Pulse < prakriti_backup.sql
```

## Next Steps

1. Set up the database using one of the methods above
2. Update Flask app configuration if needed
3. Test the database connection
4. Start using the database in your Flask application

For more information, see the main README.md file.
