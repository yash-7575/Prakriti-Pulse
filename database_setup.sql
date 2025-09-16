-- Prakriti Pulse Database Setup
-- This script creates the complete database with all tables and sample data

CREATE DATABASE IF NOT EXISTS Prakriti_Pulse;
USE Prakriti_Pulse;

-- Drop tables in reverse order of dependencies
DROP TABLE IF EXISTS formulations;
DROP TABLE IF EXISTS patient_profiles;
DROP TABLE IF EXISTS herb_symptom_relationships;
DROP TABLE IF EXISTS prakriti_profiles;
DROP TABLE IF EXISTS symptoms;
DROP TABLE IF EXISTS herbs;

-- 1) herbs table
CREATE TABLE herbs (
    herb_id INT AUTO_INCREMENT PRIMARY KEY,     
    herb_name_english VARCHAR(100),
    herb_name_sanskrit VARCHAR(100),
    herb_name_hindi VARCHAR(100),
    rasa VARCHAR(50),                           
    virya VARCHAR(50),                          
    vipaka VARCHAR(50),                         
    prabhava VARCHAR(100),                      
    vata_effect VARCHAR(100),
    pitta_effect VARCHAR(100),
    kapha_effect VARCHAR(100),
    part_used TEXT,
    preparation_method TEXT,
    dosage TEXT,
    contraindications TEXT,
    scientific_name VARCHAR(150),
    description TEXT
);

-- Sample inserts (10 herbs)
INSERT INTO herbs (herb_name_english, herb_name_sanskrit, herb_name_hindi, rasa, virya, vipaka, prabhava, vata_effect, pitta_effect, kapha_effect, part_used, preparation_method, dosage, contraindications, scientific_name, description)
VALUES
('Ashwagandha', 'Ashwagandha', 'अश्वगंधा', 'Bitter', 'Hot', 'Sweet', 'Rasayana (rejuvenator)', 'Balances Vata', 'May increase Pitta in excess', 'Reduces Kapha', 'Root', 'Powder/decoction', '3-6g daily', 'Avoid in pregnancy & high fever', 'Withania somnifera', 'Stress adaptogen; increases strength and stamina'),
('Tulsi', 'Tulasī', 'तुलसी', 'Pungent', 'Hot', 'Sweet', 'Immunity enhancer', 'Balances Vata', 'Reduces Pitta', 'Reduces Kapha', 'Leaves', 'Infusion/decoction', '5-10 leaves or 1-2g powder', 'None common (use caution in pregnancy)', 'Ocimum tenuiflorum', 'Anti-microbial and respiratory support'),
('Triphala', 'Triphala', 'त्रिफला', 'Astringent', 'Mild Hot', 'Sweet', 'Detoxifier', 'Balances Vata', 'Balances Pitta', 'Balances Kapha', 'Fruits (three)', 'Powder', '1-3g daily', 'Caution in diarrhea', 'Mixture of Emblica/Terminalia chebula/Terminalia bellirica', 'Digestive tonic and mild laxative'),
('Brahmi', 'Brahmī', 'ब्राह्मी', 'Bitter', 'Cooling', 'Sweet', 'Medhya (memory enhancer)', 'Calms Vata', 'Balances Pitta', 'Little effect on Kapha', 'Leaves', 'Extract/paste', '250-500mg extract', 'Avoid high doses in pregnancy', 'Bacopa monnieri', 'Used for cognitive support and mental clarity'),
('Neem', 'Nimba', 'नीम', 'Bitter', 'Cooling', 'Pungent', 'Rakta shodhana (blood purifier)', 'Reduces Vata', 'Reduces Pitta', 'Reduces Kapha', 'Leaves/bark', 'Juice/paste/decoction', '5-10ml decoction / topical use', 'Avoid prolonged internal use in pregnancy', 'Azadirachta indica', 'Antimicrobial; used for skin conditions'),
('Amla', 'Amalaki', 'आंवला', 'Sour', 'Cooling', 'Sweet', 'Rejuvenator & antioxidant', 'Balances Vata', 'Balances Pitta', 'Balances Kapha', 'Fruit', 'Juice/powder', '10-20ml juice or 1-3g powder', 'May aggravate hyperacidity in some', 'Phyllanthus emblica', 'High in Vitamin C; supports digestion & immunity'),
('Shatavari', 'Śatavari', 'शतावरी', 'Sweet', 'Cooling', 'Sweet', 'Female tonic (reproductive support)', 'Balances Vata', 'Reduces Pitta', 'May increase Kapha', 'Root/rhizome', 'Powder/decoction', '3-6g daily', 'Caution in estrogen-sensitive conditions', 'Asparagus racemosus', 'Supports female reproductive health & lactation'),
('Guduchi', 'Gudūci', 'गुडूची', 'Bitter', 'Hot', 'Sweet', 'Immunity & detox', 'Balances Vata', 'Balances Pitta', 'Balances Kapha', 'Stem', 'Decoction/extract', '5-15ml decoction', 'Avoid high doses in pregnancy', 'Tinospora cordifolia', 'Immunomodulator and antipyretic'),
('Haritaki', 'Harītakī', 'हरितकी', 'Astringent', 'Hot', 'Sweet', 'Digestive corrective', 'Balances Vata', 'Balances Pitta', 'Balances Kapha', 'Fruit', 'Powder/decoction', '1-3g daily', 'Avoid in pregnancy', 'Terminalia chebula', 'Promotes healthy digestion and bowel movements'),
('Arjuna', 'Arjunā', 'अर्जुन', 'Bitter', 'Cooling', 'Pungent', 'Cardiac tonic', 'Reduces Vata', 'Balances Pitta', 'Reduces Kapha', 'Bark', 'Decoction/powder', '3-6g daily', 'Caution if low blood pressure', 'Terminalia arjuna', 'Used for heart support and circulation');

-- 2) symptoms table
CREATE TABLE symptoms (
    symptom_id INT AUTO_INCREMENT PRIMARY KEY,
    symptom_name VARCHAR(150),
    symptom_category VARCHAR(100),
    associated_dosha VARCHAR(50),
    severity_level VARCHAR(50),
    body_system VARCHAR(100),
    description TEXT,
    synonyms TEXT
);

-- Sample symptom inserts (10)
INSERT INTO symptoms (symptom_name, symptom_category, associated_dosha, severity_level, body_system, description, synonyms)
VALUES
('Headache', 'Neurological', 'Pitta', 'Moderate', 'Nervous system', 'Pain located in head or scalp area', 'Cephalalgia'),
('Indigestion', 'Digestive', 'Kapha', 'Mild', 'Digestive system', 'Discomfort after eating; bloating', 'Dyspepsia'),
('Fatigue', 'General', 'Vata', 'High', 'Whole body', 'Persistent tiredness and low energy', 'Exhaustion'),
('Acidity', 'Digestive', 'Pitta', 'Moderate', 'Digestive system', 'Burning sensation in stomach/oesophagus', 'Heartburn'),
('Joint Pain', 'Musculoskeletal', 'Vata', 'Severe', 'Skeletal system', 'Pain, stiffness in joints', 'Arthralgia'),
('Cough', 'Respiratory', 'Kapha', 'Mild', 'Respiratory system', 'Expulsion of air with sound, may be dry/productive', 'Tussis'),
('Skin Rash', 'Dermatological', 'Pitta', 'Moderate', 'Integumentary system', 'Red, itchy skin patches', 'Dermatitis'),
('Fever', 'Infectious', 'Pitta', 'High', 'Whole body', 'Raised body temperature often with malaise', 'Pyrexia'),
('Constipation', 'Digestive', 'Vata', 'Moderate', 'Digestive system', 'Infrequent or difficult bowel movements', 'Obstipation'),
('Insomnia', 'Neurological', 'Vata', 'High', 'Nervous system', 'Difficulty initiating or maintaining sleep', 'Sleeplessness');

-- 3) prakriti_profiles table
CREATE TABLE prakriti_profiles (
    profile_id INT AUTO_INCREMENT PRIMARY KEY,
    vata_score INT,
    pitta_score INT,
    kapha_score INT,
    dominant_dosha VARCHAR(50),
    constitution_type VARCHAR(100),
    characteristics TEXT,
    common_ailments TEXT,
    recommended_lifestyle TEXT
);

-- Sample inserts (10 profiles)
INSERT INTO prakriti_profiles (vata_score, pitta_score, kapha_score, dominant_dosha, constitution_type, characteristics, common_ailments, recommended_lifestyle)
VALUES
(70, 20, 10, 'Vata', 'Single (Vata)', 'Thin build, variable appetite, creative, quick thinker', 'Insomnia, gas, dryness, joint pain', 'Warm routine, grounding foods, oil massage'),
(20, 75, 5, 'Pitta', 'Single (Pitta)', 'Medium build, strong digestion, driven temperament', 'Acidity, inflammation, skin rashes', 'Cool foods, avoid spicy, regular rest'),
(15, 20, 75, 'Kapha', 'Single (Kapha)', 'Sturdy build, calm, steady appetite', 'Obesity, congestion, lethargy', 'Stimulating activity, light diet, dry foods'),
(50, 40, 10, 'Vata-Pitta', 'Dual (Vata-Pitta)', 'Active and creative with strong digestion at times', 'Migraines, acidity', 'Balanced warm diet, avoid extremes'),
(30, 60, 10, 'Pitta-Vata', 'Dual (Pitta-Vata)', 'Ambitious yet anxious', 'Acidity, stress-related issues', 'Cooling routines, meditation, avoid heat'),
(10, 40, 60, 'Kapha-Pitta', 'Dual (Kapha-Pitta)', 'Slow metabolism with occasional inflammation', 'Congestion, weight gain', 'Light exercises, avoid cold foods'),
(45, 30, 25, 'Vata', 'Predominantly Vata', 'Variable moods, dry skin', 'Constipation, insomnia', 'Warm nourishing diet, oil intake'),
(25, 30, 45, 'Kapha', 'Predominantly Kapha', 'Calm, slow, stable', 'Cough, sluggish digestion', 'Stimulating herbs, exercise'),
(35, 50, 15, 'Pitta', 'Predominantly Pitta', 'Focused, energetic, warm body temperature', 'Skin rashes, acidity', 'Cooling herbs, regular breaks'),
(40, 35, 25, 'Vata', 'Mixed Vata', 'Quick to learn, quick to forget', 'Stress, fatigue', 'Grounding routine, regular sleep schedule');

-- 4) herb_symptom_relationships
CREATE TABLE herb_symptom_relationships (
    relationship_id INT AUTO_INCREMENT PRIMARY KEY,
    herb_id INT,
    symptom_id INT,
    effectiveness_score DECIMAL(3,2), -- 0.00 - 1.00 scale
    classical_reference TEXT,
    dosage_for_symptom TEXT,
    preparation_method TEXT,
    duration_of_treatment TEXT,
    supporting_herbs TEXT,
    FOREIGN KEY (herb_id) REFERENCES herbs(herb_id) ON DELETE CASCADE,
    FOREIGN KEY (symptom_id) REFERENCES symptoms(symptom_id) ON DELETE CASCADE
);

-- Sample inserts (10 mappings)
INSERT INTO herb_symptom_relationships (herb_id, symptom_id, effectiveness_score, classical_reference, dosage_for_symptom, preparation_method, duration_of_treatment, supporting_herbs)
VALUES
(1, 3, 0.90, 'Charaka Samhita, Vimana Sthana', '3-6g powdered root daily', 'Powder with warm milk', '30 days', 'Ashwagandha + Amla'),
(2, 6, 0.85, 'Sushruta Samhita, Sutrasthana', '5-10 leaves infusion twice daily', 'Decoction/infusion', '7-14 days', 'Tulsi + Ginger'),
(3, 9, 0.88, 'Ashtanga Hridayam', '1-3g before sleep', 'Powder with warm water', '2-4 weeks', 'Triphala + Haritaki'),
(4, 10, 0.80, 'Charaka, Chikitsa Sthana', '250-500mg extract in morning', 'Extract/tonic', '4 weeks', 'Brahmi + Shankhpushpi'),
(5, 7, 0.95, 'Bhavaprakasha Nighantu', 'Topical paste/juice 2-3 times daily', 'Paste/juice', '2 weeks topical', 'Neem + Turmeric'),
(6, 4, 0.82, 'Charaka Samhita', '10-20ml fresh juice', 'Fresh juice or powder', '2-3 weeks', 'Amla + Haritaki'),
(7, 5, 0.78, 'Sushruta', '3-6g powdered root twice daily', 'Decoction/powder', '6-8 weeks', 'Shatavari + Guggulu'),
(8, 8, 0.83, 'Bhavaprakasha', '15ml decoction', 'Decoction', '5-7 days', 'Guduchi + Tulsi'),
(9, 2, 0.86, 'Ashtanga Hridayam', '1-2g before meal', 'Powder', '10-21 days', 'Haritaki + Triphala'),
(10, 1, 0.75, 'Charaka', '3-6g bark decoction', 'Decoction', '2-4 weeks', 'Arjuna + Brahmi');

-- 5) patient_profiles
CREATE TABLE patient_profiles (
    patient_id INT AUTO_INCREMENT PRIMARY KEY,
    age INT,
    gender VARCHAR(10),
    prakriti_type VARCHAR(50),
    current_symptoms TEXT, -- comma-separated or JSON
    symptom_severity VARCHAR(50),
    treatment_history TEXT,
    effectiveness_rating DECIMAL(3,2),
    practitioner_notes TEXT
);

-- Sample inserts (10 patient_profiles)
INSERT INTO patient_profiles (age, gender, prakriti_type, current_symptoms, symptom_severity, treatment_history, effectiveness_rating, practitioner_notes)
VALUES
(28, 'Male', 'Vata', 'Joint Pain, Fatigue', 'High', 'Used NSAIDs intermittently; physiotherapy', 0.65, 'Vata aggravation after change in climate; recommend warming diet'),
(34, 'Female', 'Pitta', 'Acidity, Skin Rash', 'Moderate', 'Tried antacids and topical steroid', 0.55, 'Pitta tendency; avoid spicy food; neem-based topical suggested'),
(45, 'Male', 'Kapha', 'Indigestion, Constipation', 'Mild', 'Occasional antacids', 0.60, 'Recommend Triphala at bedtime and light exercise'),
(30, 'Female', 'Vata-Pitta', 'Insomnia, Headache', 'High', 'Sleep hygiene attempted', 0.50, 'Brahmi decoction suggested; reduce screen time'),
(50, 'Male', 'Pitta', 'Fever, Acidity', 'High', 'Paracetamol used', 0.70, 'Guduchi decoction for immunity advised'),
(26, 'Female', 'Kapha', 'Cough', 'Mild', 'Steam inhalation', 0.60, 'Tulsi and honey remedy recommended'),
(38, 'Male', 'Vata', 'Constipation, Joint Pain', 'Moderate', 'Fiber supplement', 0.58, 'Triphala + dietary improvements advised'),
(42, 'Female', 'Pitta', 'Skin Rash, Fatigue', 'Moderate', 'Topical creams', 0.52, 'Systemic cooling regimen suggested'),
(29, 'Male', 'Kapha', 'Indigestion, Obesity', 'Moderate', 'Diet control', 0.54, 'Amla and exercise regimen recommended'),
(31, 'Female', 'Vata', 'Headache, Insomnia', 'High', 'Melatonin occasional', 0.49, 'Calming herbs and bedtime routine advised');

-- 6) formulations
CREATE TABLE formulations (
    formulation_id INT AUTO_INCREMENT PRIMARY KEY,
    formulation_name VARCHAR(150),
    herb_ids TEXT,           -- CSV of herb_ids
    proportions TEXT,        -- e.g., "1:1:2"
    indication TEXT,
    preparation_method TEXT,
    classical_reference TEXT,
    modern_research TEXT,
    availability TEXT
);

-- Sample inserts (10 formulations)
INSERT INTO formulations (formulation_name, herb_ids, proportions, indication, preparation_method, classical_reference, modern_research, availability)
VALUES
('Chyawanprash', '6,3,9', '2:1:1', 'General immunity & rejuvenation', 'Herbs boiled in decoction, combined with ghee and jaggery', 'Charaka Samhita', 'Several antioxidant studies available', 'Commercial & homemade'),
('Triphala Churna', '3,9,6','1:1:1', 'Digestive health, constipation', 'Powdered mix of three fruits', 'Ashtanga Hridayam', 'Digestive health trials exist', 'Commercial & homemade'),
('Ashwagandha Churna', '1', '1', 'Stress, fatigue', 'Powdered root; taken with warm milk', 'Charaka', 'Adaptogen studies present', 'Widely available'),
('Brahmi Tonic', '4', '1', 'Memory & insomnia', 'Alcohol/water extract or syrup', 'Sushruta', 'Cognitive function studies ongoing', 'Herbal tonics available'),
('Neem Paste', '5', '1', 'Topical skin conditions', 'Fresh leaf paste applied topically', 'Bhavaprakasha', 'Antimicrobial studies present', 'Home & topical products'),
('Amla Juice', '6', '1', 'Rejuvenator and digestive support', 'Fresh cold-pressed juice', 'Charaka', 'Antioxidant research noted', 'Commercial & fresh markets'),
('Shatavari Syrup', '7', '1', 'Female reproductive tonic', 'Decoction concentrated to syrup', 'Bhavaprakasha', 'Limited clinical studies', 'Commercial syrups'),
('Guduchi Decoction', '8', '1', 'Fever and immune support', 'Decoction of stem', 'Ashtanga Hridayam', 'Immunomodulatory studies', 'Prepared fresh'),
('Haritaki Powder', '9', '1', 'Constipation and digestive cleansing', 'Powder taken with warm water', 'Charaka', 'Laxative property studies', 'Commercial powders'),
('Arjuna Decoction', '10', '1', 'Cardiac support and angina', 'Bark decoction', 'Sushruta', 'Cardio-protective research small trials', 'Extracts and supplements');

-- Display all tables with sample data
SELECT 'HERBS TABLE' as table_name;
SELECT * FROM herbs;

SELECT 'SYMPTOMS TABLE' as table_name;
SELECT * FROM symptoms;

SELECT 'PRAKRITI PROFILES TABLE' as table_name;
SELECT * FROM prakriti_profiles;

SELECT 'HERB-SYMPTOM RELATIONSHIPS TABLE' as table_name;
SELECT * FROM herb_symptom_relationships;

SELECT 'PATIENT PROFILES TABLE' as table_name;
SELECT * FROM patient_profiles;

SELECT 'FORMULATIONS TABLE' as table_name;
SELECT * FROM formulations;

-- Database setup complete
SELECT 'Database setup completed successfully!' as status;
