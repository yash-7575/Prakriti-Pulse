#!/usr/bin/env python3
"""
Script to expand Ayurveda GNN dataset with unique, valid entries.
Generates 2500-3000 unique entries for each node type and proportional edges.
"""

import csv
import random
from collections import defaultdict

# Ayurveda-valid data templates
DOSHAS = ['Vata', 'Pitta', 'Kapha']
SEVERITY_LEVELS = ['Low', 'Medium', 'High']
BODY_SYSTEMS = [
    'Nervous system', 'Digestive system', 'Respiratory system', 
    'Cardiovascular system', 'Musculoskeletal system', 'Integumentary system',
    'Endocrine system', 'Urinary system', 'Reproductive system', 'Immune system',
    'Metabolic system', 'Mental'
]

# Comprehensive health conditions (Ayurveda-valid)
HEALTH_CONDITIONS = [
    # Digestive
    ('Gastroparesis', 'Delayed stomach emptying', 'Vata', 'Kapha', 'Digestive system', 'High'),
    ('Dyspepsia', 'Indigestion and discomfort', 'Pitta', 'Vata', 'Digestive system', 'Medium'),
    ('Gastritis Chronic', 'Long-term stomach inflammation', 'Pitta', 'Kapha', 'Digestive system', 'Medium'),
    ('Duodenitis', 'Inflammation of duodenum', 'Pitta', 'Vata', 'Digestive system', 'Medium'),
    ('Enteritis', 'Small intestine inflammation', 'Vata', 'Pitta', 'Digestive system', 'Medium'),
    ('Colitis', 'Colon inflammation', 'Vata', 'Kapha', 'Digestive system', 'High'),
    ('Proctitis', 'Rectal inflammation', 'Pitta', 'Vata', 'Digestive system', 'Medium'),
    ('Ileitis', 'Ileum inflammation', 'Vata', 'Pitta', 'Digestive system', 'Medium'),
    ('Jejunitis', 'Jejunum inflammation', 'Vata', 'Pitta', 'Digestive system', 'Medium'),
    ('Pancreatic Insufficiency', 'Inadequate enzyme production', 'Pitta', 'Kapha', 'Digestive system', 'High'),
    ('Biliary Dyskinesia', 'Abnormal bile flow', 'Pitta', 'Vata', 'Digestive system', 'Medium'),
    ('Sphincter of Oddi Dysfunction', 'Bile duct sphincter issues', 'Pitta', 'Vata', 'Digestive system', 'High'),
    ('Bile Reflux', 'Bile backing up into stomach', 'Pitta', 'Vata', 'Digestive system', 'Medium'),
    ('Gastric Atrophy', 'Stomach lining thinning', 'Vata', 'Kapha', 'Digestive system', 'High'),
    ('Intestinal Metaplasia', 'Abnormal cell changes', 'Pitta', 'Kapha', 'Digestive system', 'High'),
    ('Barrett Esophagus', 'Esophageal cell changes', 'Pitta', 'Vata', 'Digestive system', 'High'),
    ('Esophagitis', 'Esophageal inflammation', 'Pitta', 'Vata', 'Digestive system', 'Medium'),
    ('Eosinophilic Esophagitis', 'Allergic esophageal inflammation', 'Pitta', 'Kapha', 'Digestive system', 'High'),
    ('Functional Dyspepsia', 'Persistent indigestion', 'Vata', 'Pitta', 'Digestive system', 'Medium'),
    ('Non-ulcer Dyspepsia', 'Indigestion without ulcers', 'Vata', 'Pitta', 'Digestive system', 'Low'),
    # Respiratory
    ('Chronic Obstructive Pulmonary Disease', 'Progressive lung disease', 'Kapha', 'Vata', 'Respiratory system', 'High'),
    ('Pulmonary Hypertension', 'High blood pressure in lungs', 'Vata', 'Pitta', 'Respiratory system', 'High'),
    ('Interstitial Lung Disease', 'Lung tissue scarring', 'Vata', 'Kapha', 'Respiratory system', 'High'),
    ('Pulmonary Fibrosis', 'Lung scarring', 'Vata', 'Kapha', 'Respiratory system', 'High'),
    ('Bronchiectasis', 'Permanent airway damage', 'Kapha', 'Pitta', 'Respiratory system', 'High'),
    ('Pleural Effusion', 'Fluid around lungs', 'Kapha', 'Vata', 'Respiratory system', 'High'),
    ('Pneumothorax', 'Collapsed lung', 'Vata', 'Kapha', 'Respiratory system', 'High'),
    ('Atelectasis', 'Lung collapse', 'Vata', 'Kapha', 'Respiratory system', 'Medium'),
    ('Respiratory Distress Syndrome', 'Severe breathing difficulty', 'Kapha', 'Vata', 'Respiratory system', 'High'),
    ('Pulmonary Edema', 'Fluid in lungs', 'Kapha', 'Pitta', 'Respiratory system', 'High'),
    ('Laryngotracheitis', 'Throat and windpipe inflammation', 'Kapha', 'Vata', 'Respiratory system', 'Medium'),
    ('Tracheitis', 'Windpipe inflammation', 'Kapha', 'Vata', 'Respiratory system', 'Medium'),
    ('Bronchiolitis', 'Small airway inflammation', 'Kapha', 'Vata', 'Respiratory system', 'Medium'),
    ('Alveolitis', 'Air sac inflammation', 'Kapha', 'Pitta', 'Respiratory system', 'High'),
    ('Pleuritis', 'Lung lining inflammation', 'Vata', 'Pitta', 'Respiratory system', 'High'),
    # Cardiovascular
    ('Atherosclerosis', 'Artery hardening', 'Vata', 'Kapha', 'Cardiovascular system', 'High'),
    ('Peripheral Vascular Disease', 'Blood vessel narrowing', 'Vata', 'Kapha', 'Cardiovascular system', 'High'),
    ('Venous Insufficiency', 'Poor vein function', 'Vata', 'Kapha', 'Cardiovascular system', 'Medium'),
    ('Deep Vein Thrombosis', 'Blood clot in vein', 'Vata', 'Pitta', 'Cardiovascular system', 'High'),
    ('Varicose Veins', 'Enlarged veins', 'Vata', 'Kapha', 'Cardiovascular system', 'Low'),
    ('Thrombophlebitis', 'Vein inflammation with clot', 'Vata', 'Pitta', 'Cardiovascular system', 'High'),
    ('Cardiomyopathy', 'Heart muscle disease', 'Vata', 'Kapha', 'Cardiovascular system', 'High'),
    ('Dilated Cardiomyopathy', 'Enlarged heart', 'Vata', 'Kapha', 'Cardiovascular system', 'High'),
    ('Hypertrophic Cardiomyopathy', 'Thickened heart muscle', 'Vata', 'Kapha', 'Cardiovascular system', 'High'),
    ('Restrictive Cardiomyopathy', 'Stiff heart muscle', 'Vata', 'Kapha', 'Cardiovascular system', 'High'),
    ('Myocarditis', 'Heart muscle inflammation', 'Pitta', 'Vata', 'Cardiovascular system', 'High'),
    ('Endocarditis', 'Heart lining infection', 'Pitta', 'Kapha', 'Cardiovascular system', 'High'),
    ('Pericarditis', 'Heart sac inflammation', 'Pitta', 'Vata', 'Cardiovascular system', 'High'),
    ('Atrial Fibrillation', 'Irregular heart rhythm', 'Vata', 'Pitta', 'Cardiovascular system', 'High'),
    ('Atrial Flutter', 'Rapid heart rhythm', 'Vata', 'Pitta', 'Cardiovascular system', 'High'),
    ('Ventricular Tachycardia', 'Fast heart rhythm', 'Vata', 'Pitta', 'Cardiovascular system', 'High'),
    ('Bradycardia', 'Slow heart rate', 'Vata', 'Kapha', 'Cardiovascular system', 'Medium'),
    ('Heart Block', 'Electrical conduction issues', 'Vata', 'Kapha', 'Cardiovascular system', 'High'),
    ('Sick Sinus Syndrome', 'Sinus node dysfunction', 'Vata', 'Kapha', 'Cardiovascular system', 'High'),
    ('Wolff-Parkinson-White Syndrome', 'Extra electrical pathway', 'Vata', 'Pitta', 'Cardiovascular system', 'High'),
    # Neurological
    ('Multiple Sclerosis', 'Autoimmune nerve disease', 'Vata', 'Kapha', 'Nervous system', 'High'),
    ('Amyotrophic Lateral Sclerosis', 'Motor neuron disease', 'Vata', 'Pitta', 'Nervous system', 'High'),
    ('Huntington Disease', 'Genetic brain disorder', 'Vata', 'Pitta', 'Nervous system', 'High'),
    ('Myasthenia Gravis', 'Muscle weakness', 'Vata', 'Kapha', 'Nervous system', 'High'),
    ('Guillain-Barre Syndrome', 'Immune nerve attack', 'Vata', 'Pitta', 'Nervous system', 'High'),
    ('Peripheral Neuropathy', 'Nerve damage', 'Vata', 'Kapha', 'Nervous system', 'High'),
    ('Diabetic Neuropathy', 'Nerve damage from diabetes', 'Vata', 'Pitta', 'Nervous system', 'High'),
    ('Trigeminal Neuralgia', 'Facial nerve pain', 'Vata', 'Pitta', 'Nervous system', 'High'),
    ('Bell Palsy', 'Facial paralysis', 'Vata', 'Kapha', 'Nervous system', 'Medium'),
    ('Radiculopathy', 'Nerve root compression', 'Vata', 'Kapha', 'Nervous system', 'High'),
    ('Cervical Radiculopathy', 'Neck nerve compression', 'Vata', 'Kapha', 'Nervous system', 'High'),
    ('Lumbar Radiculopathy', 'Lower back nerve compression', 'Vata', 'Kapha', 'Nervous system', 'High'),
    ('Carpal Tunnel Syndrome', 'Wrist nerve compression', 'Vata', 'Kapha', 'Nervous system', 'Medium'),
    ('Ulnar Neuropathy', 'Elbow nerve compression', 'Vata', 'Kapha', 'Nervous system', 'Medium'),
    ('Meralgia Paresthetica', 'Thigh nerve compression', 'Vata', 'Kapha', 'Nervous system', 'Medium'),
    ('Tarsal Tunnel Syndrome', 'Ankle nerve compression', 'Vata', 'Kapha', 'Nervous system', 'Medium'),
    ('Restless Legs Syndrome', 'Urge to move legs', 'Vata', 'Kapha', 'Nervous system', 'Medium'),
    ('Periodic Limb Movement Disorder', 'Involuntary leg movements', 'Vata', 'Kapha', 'Nervous system', 'Medium'),
    ('Narcolepsy', 'Excessive daytime sleepiness', 'Kapha', 'Vata', 'Nervous system', 'High'),
    # Mental Health
    ('Generalized Anxiety Disorder', 'Persistent anxiety', 'Vata', 'Pitta', 'Mental', 'High'),
    ('Panic Disorder', 'Recurrent panic attacks', 'Vata', 'Pitta', 'Mental', 'High'),
    ('Social Anxiety Disorder', 'Fear of social situations', 'Vata', 'Pitta', 'Mental', 'Medium'),
    ('Agoraphobia', 'Fear of open spaces', 'Vata', 'Pitta', 'Mental', 'High'),
    ('Specific Phobia', 'Intense fear of specific things', 'Vata', 'Pitta', 'Mental', 'Medium'),
    ('Separation Anxiety', 'Fear of separation', 'Vata', 'Kapha', 'Mental', 'Medium'),
    ('Selective Mutism', 'Inability to speak in situations', 'Vata', 'Kapha', 'Mental', 'Medium'),
    ('Major Depressive Disorder', 'Severe depression', 'Vata', 'Kapha', 'Mental', 'High'),
    ('Persistent Depressive Disorder', 'Long-term depression', 'Vata', 'Kapha', 'Mental', 'High'),
    ('Seasonal Affective Disorder', 'Seasonal depression', 'Vata', 'Kapha', 'Mental', 'Medium'),
    ('Premenstrual Dysphoric Disorder', 'Severe PMS', 'Vata', 'Pitta', 'Mental', 'High'),
    ('Disruptive Mood Dysregulation', 'Severe temper outbursts', 'Vata', 'Pitta', 'Mental', 'High'),
    ('Body Dysmorphic Disorder', 'Preoccupation with appearance', 'Vata', 'Pitta', 'Mental', 'High'),
    ('Trichotillomania', 'Hair pulling disorder', 'Vata', 'Pitta', 'Mental', 'Medium'),
    ('Excoriation Disorder', 'Skin picking disorder', 'Vata', 'Pitta', 'Mental', 'Medium'),
    # Skin Conditions
    ('Dermatitis', 'Skin inflammation', 'Vata', 'Kapha', 'Integumentary system', 'Medium'),
    ('Contact Dermatitis', 'Skin reaction to contact', 'Pitta', 'Kapha', 'Integumentary system', 'Medium'),
    ('Atopic Dermatitis', 'Chronic skin inflammation', 'Vata', 'Kapha', 'Integumentary system', 'High'),
    ('Seborrheic Dermatitis', 'Oily skin inflammation', 'Pitta', 'Kapha', 'Integumentary system', 'Medium'),
    ('Nummular Dermatitis', 'Coin-shaped skin patches', 'Vata', 'Kapha', 'Integumentary system', 'Medium'),
    ('Stasis Dermatitis', 'Leg skin inflammation', 'Vata', 'Kapha', 'Integumentary system', 'Medium'),
    ('Dyshidrotic Eczema', 'Blistering hand eczema', 'Pitta', 'Kapha', 'Integumentary system', 'Medium'),
    ('Lichen Planus', 'Inflammatory skin condition', 'Vata', 'Pitta', 'Integumentary system', 'High'),
    ('Lichen Simplex Chronicus', 'Thickened skin patches', 'Vata', 'Kapha', 'Integumentary system', 'Medium'),
    ('Pityriasis Rosea', 'Rash with scaling', 'Pitta', 'Kapha', 'Integumentary system', 'Low'),
    ('Pityriasis Versicolor', 'Fungal skin infection', 'Kapha', 'Pitta', 'Integumentary system', 'Low'),
    ('Tinea', 'Fungal skin infection', 'Kapha', 'Pitta', 'Integumentary system', 'Medium'),
    ('Tinea Corporis', 'Ringworm', 'Kapha', 'Pitta', 'Integumentary system', 'Medium'),
    ('Tinea Cruris', 'Jock itch', 'Kapha', 'Pitta', 'Integumentary system', 'Medium'),
    ('Tinea Pedis', 'Athlete foot', 'Kapha', 'Pitta', 'Integumentary system', 'Medium'),
    ('Onychomycosis', 'Nail fungus', 'Kapha', 'Vata', 'Integumentary system', 'Medium'),
    ('Paronychia', 'Nail fold infection', 'Pitta', 'Kapha', 'Integumentary system', 'Medium'),
    ('Folliculitis', 'Hair follicle infection', 'Pitta', 'Kapha', 'Integumentary system', 'Medium'),
    ('Furuncle', 'Boil', 'Pitta', 'Kapha', 'Integumentary system', 'Medium'),
    ('Carbuncle', 'Cluster of boils', 'Pitta', 'Kapha', 'Integumentary system', 'High'),
    # Musculoskeletal
    ('Fibromyalgia', 'Widespread muscle pain', 'Vata', 'Kapha', 'Musculoskeletal system', 'High'),
    ('Myofascial Pain Syndrome', 'Muscle trigger points', 'Vata', 'Kapha', 'Musculoskeletal system', 'Medium'),
    ('Temporomandibular Joint Disorder', 'Jaw joint dysfunction', 'Vata', 'Kapha', 'Musculoskeletal system', 'Medium'),
    ('Cervical Spondylosis', 'Neck arthritis', 'Vata', 'Kapha', 'Musculoskeletal system', 'High'),
    ('Lumbar Spondylosis', 'Lower back arthritis', 'Vata', 'Kapha', 'Musculoskeletal system', 'High'),
    ('Ankylosing Spondylitis', 'Spine inflammation', 'Vata', 'Kapha', 'Musculoskeletal system', 'High'),
    ('Reactive Arthritis', 'Joint inflammation after infection', 'Vata', 'Pitta', 'Musculoskeletal system', 'High'),
    ('Psoriatic Arthritis', 'Arthritis with psoriasis', 'Vata', 'Kapha', 'Musculoskeletal system', 'High'),
    ('Gouty Arthritis', 'Uric acid crystal arthritis', 'Vata', 'Pitta', 'Musculoskeletal system', 'High'),
    ('Pseudogout', 'Calcium crystal arthritis', 'Vata', 'Pitta', 'Musculoskeletal system', 'Medium'),
    ('Bursitis', 'Joint cushion inflammation', 'Vata', 'Kapha', 'Musculoskeletal system', 'Medium'),
    ('Tendinitis', 'Tendon inflammation', 'Vata', 'Kapha', 'Musculoskeletal system', 'Medium'),
    ('Tendinosis', 'Tendon degeneration', 'Vata', 'Kapha', 'Musculoskeletal system', 'High'),
    ('Rotator Cuff Tear', 'Shoulder tendon tear', 'Vata', 'Kapha', 'Musculoskeletal system', 'High'),
    ('Frozen Shoulder', 'Shoulder stiffness', 'Vata', 'Kapha', 'Musculoskeletal system', 'High'),
    ('Tennis Elbow', 'Elbow tendon inflammation', 'Vata', 'Kapha', 'Musculoskeletal system', 'Medium'),
    ('Golfer Elbow', 'Inner elbow inflammation', 'Vata', 'Kapha', 'Musculoskeletal system', 'Medium'),
    ('Carpal Tunnel Syndrome', 'Wrist nerve compression', 'Vata', 'Kapha', 'Musculoskeletal system', 'Medium'),
    ('De Quervain Tenosynovitis', 'Thumb tendon inflammation', 'Vata', 'Kapha', 'Musculoskeletal system', 'Medium'),
    ('Plantar Fasciitis', 'Heel pain', 'Vata', 'Kapha', 'Musculoskeletal system', 'Medium'),
    # Endocrine
    ('Type 1 Diabetes', 'Autoimmune diabetes', 'Pitta', 'Kapha', 'Endocrine system', 'High'),
    ('Type 2 Diabetes', 'Insulin resistance diabetes', 'Pitta', 'Kapha', 'Endocrine system', 'High'),
    ('Gestational Diabetes', 'Pregnancy diabetes', 'Pitta', 'Kapha', 'Endocrine system', 'High'),
    ('Prediabetes', 'Elevated blood sugar', 'Pitta', 'Kapha', 'Endocrine system', 'Medium'),
    ('Metabolic Syndrome', 'Cluster of metabolic conditions', 'Pitta', 'Kapha', 'Endocrine system', 'High'),
    ('Polycystic Ovary Syndrome', 'Hormonal disorder', 'Kapha', 'Vata', 'Endocrine system', 'High'),
    ('Cushing Syndrome', 'Excess cortisol', 'Vata', 'Pitta', 'Endocrine system', 'High'),
    ('Addison Disease', 'Adrenal insufficiency', 'Vata', 'Kapha', 'Endocrine system', 'High'),
    ('Graves Disease', 'Overactive thyroid', 'Vata', 'Pitta', 'Endocrine system', 'High'),
    ('Hashimoto Thyroiditis', 'Underactive thyroid', 'Vata', 'Kapha', 'Endocrine system', 'High'),
    ('Thyroid Nodules', 'Thyroid lumps', 'Kapha', 'Vata', 'Endocrine system', 'Medium'),
    ('Goiter', 'Enlarged thyroid', 'Kapha', 'Vata', 'Endocrine system', 'Medium'),
    ('Hyperparathyroidism', 'Excess parathyroid hormone', 'Vata', 'Pitta', 'Endocrine system', 'High'),
    ('Hypoparathyroidism', 'Low parathyroid hormone', 'Vata', 'Kapha', 'Endocrine system', 'High'),
    ('Pheochromocytoma', 'Adrenal tumor', 'Vata', 'Pitta', 'Endocrine system', 'High'),
    ('Insulinoma', 'Pancreatic insulin tumor', 'Pitta', 'Kapha', 'Endocrine system', 'High'),
    ('Acromegaly', 'Excess growth hormone', 'Kapha', 'Vata', 'Endocrine system', 'High'),
    ('Gigantism', 'Excessive growth', 'Kapha', 'Vata', 'Endocrine system', 'High'),
    ('Dwarfism', 'Growth hormone deficiency', 'Vata', 'Kapha', 'Endocrine system', 'High'),
    ('Pituitary Adenoma', 'Pituitary tumor', 'Vata', 'Pitta', 'Endocrine system', 'High'),
    # Urinary
    ('Chronic Kidney Disease', 'Progressive kidney dysfunction', 'Vata', 'Kapha', 'Urinary system', 'High'),
    ('Acute Kidney Injury', 'Sudden kidney failure', 'Vata', 'Pitta', 'Urinary system', 'High'),
    ('Nephrotic Syndrome', 'Kidney protein loss', 'Vata', 'Kapha', 'Urinary system', 'High'),
    ('Nephritic Syndrome', 'Kidney inflammation', 'Pitta', 'Vata', 'Urinary system', 'High'),
    ('Glomerulonephritis', 'Kidney filter inflammation', 'Pitta', 'Vata', 'Urinary system', 'High'),
    ('Pyelonephritis', 'Kidney infection', 'Pitta', 'Kapha', 'Urinary system', 'High'),
    ('Interstitial Cystitis', 'Chronic bladder pain', 'Vata', 'Pitta', 'Urinary system', 'High'),
    ('Overactive Bladder', 'Urinary urgency', 'Vata', 'Kapha', 'Urinary system', 'Medium'),
    ('Neurogenic Bladder', 'Nerve-related bladder issues', 'Vata', 'Kapha', 'Urinary system', 'High'),
    ('Bladder Outlet Obstruction', 'Blocked urine flow', 'Vata', 'Kapha', 'Urinary system', 'High'),
    ('Urethral Stricture', 'Narrowed urethra', 'Vata', 'Kapha', 'Urinary system', 'High'),
    ('Hydronephrosis', 'Kidney swelling', 'Kapha', 'Vata', 'Urinary system', 'High'),
    ('Renal Calculi', 'Kidney stones', 'Vata', 'Kapha', 'Urinary system', 'High'),
    ('Ureteral Calculi', 'Ureter stones', 'Vata', 'Kapha', 'Urinary system', 'High'),
    ('Bladder Calculi', 'Bladder stones', 'Vata', 'Kapha', 'Urinary system', 'High'),
    ('Renal Artery Stenosis', 'Narrowed kidney artery', 'Vata', 'Kapha', 'Urinary system', 'High'),
    ('Renal Vein Thrombosis', 'Kidney vein clot', 'Vata', 'Pitta', 'Urinary system', 'High'),
    ('Polycystic Kidney Disease', 'Multiple kidney cysts', 'Vata', 'Kapha', 'Urinary system', 'High'),
    ('Medullary Sponge Kidney', 'Kidney abnormality', 'Vata', 'Kapha', 'Urinary system', 'Medium'),
    ('Renal Tubular Acidosis', 'Kidney acid imbalance', 'Vata', 'Pitta', 'Urinary system', 'High'),
    # Reproductive
    ('Endometriosis', 'Uterine tissue outside uterus', 'Vata', 'Kapha', 'Reproductive system', 'High'),
    ('Adenomyosis', 'Uterine tissue in muscle', 'Vata', 'Kapha', 'Reproductive system', 'High'),
    ('Uterine Fibroids', 'Uterine muscle tumors', 'Vata', 'Kapha', 'Reproductive system', 'Medium'),
    ('Ovarian Cysts', 'Ovarian fluid sacs', 'Kapha', 'Vata', 'Reproductive system', 'Medium'),
    ('Polycystic Ovaries', 'Multiple ovarian cysts', 'Kapha', 'Vata', 'Reproductive system', 'High'),
    ('Premature Ovarian Failure', 'Early menopause', 'Vata', 'Kapha', 'Reproductive system', 'High'),
    ('Asherman Syndrome', 'Uterine adhesions', 'Vata', 'Kapha', 'Reproductive system', 'High'),
    ('Cervical Stenosis', 'Narrowed cervix', 'Vata', 'Kapha', 'Reproductive system', 'High'),
    ('Cervical Incompetence', 'Weak cervix', 'Vata', 'Kapha', 'Reproductive system', 'High'),
    ('Pelvic Inflammatory Disease', 'Reproductive organ infection', 'Pitta', 'Kapha', 'Reproductive system', 'High'),
    ('Bartholin Cyst', 'Vaginal gland cyst', 'Kapha', 'Vata', 'Reproductive system', 'Medium'),
    ('Vulvodynia', 'Chronic vulvar pain', 'Vata', 'Pitta', 'Reproductive system', 'High'),
    ('Vaginismus', 'Vaginal muscle spasm', 'Vata', 'Kapha', 'Reproductive system', 'High'),
    ('Dyspareunia', 'Painful intercourse', 'Vata', 'Kapha', 'Reproductive system', 'High'),
    ('Erectile Dysfunction', 'Impotence', 'Vata', 'Kapha', 'Reproductive system', 'High'),
    ('Premature Ejaculation', 'Early climax', 'Vata', 'Pitta', 'Reproductive system', 'Medium'),
    ('Delayed Ejaculation', 'Delayed climax', 'Vata', 'Kapha', 'Reproductive system', 'Medium'),
    ('Priapism', 'Prolonged erection', 'Pitta', 'Vata', 'Reproductive system', 'High'),
    ('Peyronie Disease', 'Penile curvature', 'Vata', 'Kapha', 'Reproductive system', 'High'),
    ('Phimosis', 'Tight foreskin', 'Vata', 'Kapha', 'Reproductive system', 'Medium'),
    # Immune/Autoimmune
    ('Systemic Lupus Erythematosus', 'Autoimmune connective tissue disease', 'Vata', 'Pitta', 'Immune system', 'High'),
    ('Rheumatoid Arthritis', 'Autoimmune joint disease', 'Vata', 'Kapha', 'Immune system', 'High'),
    ('Sjogren Syndrome', 'Dry eyes and mouth', 'Vata', 'Pitta', 'Immune system', 'High'),
    ('Scleroderma', 'Hardening of connective tissue', 'Vata', 'Kapha', 'Immune system', 'High'),
    ('Dermatomyositis', 'Muscle and skin inflammation', 'Vata', 'Pitta', 'Immune system', 'High'),
    ('Polymyositis', 'Muscle inflammation', 'Vata', 'Pitta', 'Immune system', 'High'),
    ('Mixed Connective Tissue Disease', 'Overlapping autoimmune conditions', 'Vata', 'Pitta', 'Immune system', 'High'),
    ('Antiphospholipid Syndrome', 'Blood clotting disorder', 'Vata', 'Pitta', 'Immune system', 'High'),
    ('Behcet Disease', 'Blood vessel inflammation', 'Vata', 'Pitta', 'Immune system', 'High'),
    ('Sarcoidosis', 'Organ inflammation', 'Vata', 'Kapha', 'Immune system', 'High'),
    ('Wegener Granulomatosis', 'Vessel inflammation', 'Vata', 'Pitta', 'Immune system', 'High'),
    ('Churg-Strauss Syndrome', 'Blood vessel inflammation', 'Vata', 'Pitta', 'Immune system', 'High'),
    ('Goodpasture Syndrome', 'Lung and kidney inflammation', 'Vata', 'Pitta', 'Immune system', 'High'),
    ('Giant Cell Arteritis', 'Artery inflammation', 'Vata', 'Pitta', 'Immune system', 'High'),
    ('Takayasu Arteritis', 'Aorta inflammation', 'Vata', 'Pitta', 'Immune system', 'High'),
    ('Kawasaki Disease', 'Blood vessel inflammation in children', 'Vata', 'Pitta', 'Immune system', 'High'),
    ('Henoch-Schonlein Purpura', 'Blood vessel inflammation', 'Vata', 'Pitta', 'Immune system', 'High'),
    ('Eosinophilic Granulomatosis', 'Blood vessel inflammation', 'Vata', 'Pitta', 'Immune system', 'High'),
    ('Microscopic Polyangiitis', 'Small vessel inflammation', 'Vata', 'Pitta', 'Immune system', 'High'),
    ('Granulomatosis with Polyangiitis', 'Vessel and organ inflammation', 'Vata', 'Pitta', 'Immune system', 'High'),
]

def generate_health_conditions():
    """Generate 2500-3000 unique health conditions"""
    conditions = []
    seen_names = set()
    node_id = 1
    max_existing_id = 0
    
    # Read existing conditions
    existing_conditions = []
    try:
        with open('nodes/health_conditions.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                name = row.get('name', '').strip()
                if name and name not in seen_names:
                    seen_names.add(name)
                    # Ensure all required fields exist
                    condition = {
                        'node_id': str(node_id),
                        'name': name,
                        'description': row.get('description', ''),
                        'primary_dosha_imbalance': row.get('primary_dosha_imbalance', ''),
                        'secondary_dosha_imbalance': row.get('secondary_dosha_imbalance', ''),
                        'affected_body_systems': row.get('affected_body_systems', ''),
                        'severity_level': row.get('severity_level', 'Medium')
                    }
                    existing_conditions.append(condition)
                    max_existing_id = max(max_existing_id, int(row.get('node_id', '0')))
    except Exception as e:
        print(f"Error reading existing conditions: {e}")
        pass
    
    # Add existing unique conditions
    conditions.extend(existing_conditions)
    
    # Set starting node_id
    node_id = max_existing_id + 1 if max_existing_id > 0 else len(conditions) + 1
    
    # Generate new conditions from template
    for name, desc, prim, sec, system, sev in HEALTH_CONDITIONS:
        if name not in seen_names:
            seen_names.add(name)
            conditions.append({
                'node_id': str(node_id),
                'name': name,
                'description': desc,
                'primary_dosha_imbalance': prim,
                'secondary_dosha_imbalance': sec if sec else '',
                'affected_body_systems': system,
                'severity_level': sev
            })
            node_id += 1
    
    # Generate additional variations to reach 2500-3000
    condition_prefixes = [
        'Acute', 'Chronic', 'Recurrent', 'Severe', 'Mild', 'Moderate',
        'Primary', 'Secondary', 'Idiopathic', 'Familial', 'Congenital',
        'Acquired', 'Progressive', 'Refractory', 'Complicated'
    ]
    
    condition_suffixes = [
        'Syndrome', 'Disorder', 'Disease', 'Condition', 'Disorder Type I',
        'Disorder Type II', 'Variant', 'Form', 'Subtype'
    ]
    
    base_conditions = [
        ('Gastritis', 'Stomach inflammation', 'Pitta', 'Vata', 'Digestive system'),
        ('Colitis', 'Colon inflammation', 'Vata', 'Kapha', 'Digestive system'),
        ('Hepatitis', 'Liver inflammation', 'Pitta', 'Kapha', 'Digestive system'),
        ('Nephritis', 'Kidney inflammation', 'Pitta', 'Vata', 'Urinary system'),
        ('Arthritis', 'Joint inflammation', 'Vata', 'Kapha', 'Musculoskeletal system'),
        ('Dermatitis', 'Skin inflammation', 'Vata', 'Kapha', 'Integumentary system'),
        ('Bronchitis', 'Bronchial inflammation', 'Kapha', 'Vata', 'Respiratory system'),
        ('Pneumonitis', 'Lung inflammation', 'Kapha', 'Pitta', 'Respiratory system'),
        ('Carditis', 'Heart inflammation', 'Pitta', 'Vata', 'Cardiovascular system'),
        ('Encephalitis', 'Brain inflammation', 'Vata', 'Pitta', 'Nervous system'),
        ('Meningitis', 'Brain lining inflammation', 'Vata', 'Pitta', 'Nervous system'),
        ('Neuritis', 'Nerve inflammation', 'Vata', 'Kapha', 'Nervous system'),
        ('Myositis', 'Muscle inflammation', 'Vata', 'Pitta', 'Musculoskeletal system'),
        ('Tendinitis', 'Tendon inflammation', 'Vata', 'Kapha', 'Musculoskeletal system'),
        ('Bursitis', 'Joint cushion inflammation', 'Vata', 'Kapha', 'Musculoskeletal system'),
    ]
    
    while len(conditions) < 2500:
        # Create variations
        prefix = random.choice(condition_prefixes) if random.random() < 0.3 else ''
        base_name, base_desc, prim, sec, system = random.choice(base_conditions)
        suffix = random.choice(condition_suffixes) if random.random() < 0.2 else ''
        
        if prefix:
            name = f"{prefix} {base_name}"
        elif suffix:
            name = f"{base_name} {suffix}"
        else:
            name = base_name
        
        # Add location/type modifiers
        if random.random() < 0.2:
            locations = ['Upper', 'Lower', 'Left', 'Right', 'Bilateral', 'Unilateral']
            name = f"{random.choice(locations)} {name}"
        
        if name not in seen_names and len(name) < 100:
            seen_names.add(name)
            severity = random.choice(SEVERITY_LEVELS)
            conditions.append({
                'node_id': str(node_id),
                'name': name,
                'description': base_desc,
                'primary_dosha_imbalance': prim,
                'secondary_dosha_imbalance': sec if random.random() < 0.7 else '',
                'affected_body_systems': system,
                'severity_level': severity
            })
            node_id += 1
            
            if len(conditions) >= 3000:
                break
    
    # Write to file
    with open('nodes/health_conditions.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['node_id', 'name', 'description', 'primary_dosha_imbalance', 
                                              'secondary_dosha_imbalance', 'affected_body_systems', 'severity_level'])
        writer.writeheader()
        writer.writerows(conditions)
    
    print(f"Generated {len(conditions)} unique health conditions")
    return len(conditions)

if __name__ == '__main__':
    generate_health_conditions()

