# Comprehensive Ayurvedic Herb Recommendation Dataset

This is a complete dataset for training Graph Neural Networks (GNNs) to recommend Ayurvedic herbs based on health conditions and dosha states. The dataset contains over 500 entries across multiple categories.

## Dataset Overview

This dataset represents the relationships between various entities in Ayurveda:
- **Herbs**: 205 medicinal plants with their properties and uses
- **Health Conditions**: 200+ diseases and ailments that herbs can treat
- **Doshas**: The three fundamental energies (Vata, Pitta, Kapha) in Ayurveda
- **Symptoms**: 200+ manifestations of health conditions
- **Body Parts**: Organs and systems targeted by herbs

## Entities

1. **Herbs**: Include Ashwagandha, Turmeric, Triphala, Brahmi, Neem, Ginger, Amla, Shatavari, Guggulu, Tulsi, and 195+ more
2. **Health Conditions**: Include Insomnia, Arthritis, Digestive Disorders, Anxiety, Skin Diseases, Asthma, Diabetes, and 190+ more
3. **Doshas**: Vata, Pitta, Kapha
4. **Symptoms**: Include Fatigue, Headache, Nausea, Joint stiffness, Skin rash, Cough, and 190+ more
5. **Body Parts**: Include Brain, Heart, Liver, Lungs, Stomach, Intestines, Skin, Joints, and others

## File Structure

```
ayurveda_complete_dataset/
├── nodes/
│   ├── herbs.csv
│   ├── health_conditions.csv
│   ├── doshas.csv
│   ├── symptoms.csv
│   └── body_parts.csv
├── edges/
│   ├── herb_treats_condition.csv
│   ├── herb_balances_dosha.csv
│   ├── condition_aggravates_dosha.csv
│   ├── condition_manifests_as_symptom.csv
│   ├── herb_targets_body_part.csv
│   ├── condition_affects_body_part.csv
│   ├── dosha_governs_body_part.csv
│   └── symptom_indicates_dosha_imbalance.csv
└── README.md
```

## Usage for GNN Training

This dataset can be used to train GNN models for:
1. Herb recommendation based on health conditions
2. Personalized recommendations based on dosha states
3. Predicting herb-condition-dosha interactions
4. Understanding polyherbal formulations

The node features and edge attributes can be encoded numerically for input into GNN architectures.

## Dataset Statistics

- Total Herbs: 205
- Total Health Conditions: 200+
- Total Symptoms: 200+
- Total Body Parts: 12
- Total Doshas: 3
- Total Relationships: 1000+

This comprehensive dataset provides a rich foundation for Ayurvedic herb recommendation systems using machine learning approaches.