# Ayurvedic Herb Recommendation Dataset - Complete Summary

This comprehensive dataset contains over 500 entries for training Graph Neural Networks (GNNs) to recommend Ayurvedic herbs based on health conditions and dosha states.

## Dataset Overview

The dataset represents relationships between various entities in Ayurveda:
- **Herbs**: 205 medicinal plants with their properties and uses
- **Health Conditions**: 200+ diseases and ailments that herbs can treat
- **Doshas**: The three fundamental energies (Vata, Pitta, Kapha) in Ayurveda
- **Symptoms**: 200+ manifestations of health conditions
- **Body Parts**: 12 organs and systems targeted by herbs

## Dataset Statistics

| Entity Type | Count | Description |
|-------------|-------|-------------|
| Herbs | 205 | Medicinal plants used in Ayurveda |
| Health Conditions | 200+ | Diseases and health issues |
| Doshas | 3 | Vata, Pitta, Kapha |
| Symptoms | 200+ | Manifestations of health conditions |
| Body Parts | 12 | Organs and body systems |
| Herb-Condition Relationships | 175+ | Treatment efficacies |
| Herb-Dosha Relationships | 200+ | Dosha balancing effects |
| Condition-Dosha Relationships | 150+ | Dosha aggravation patterns |
| Condition-Symptom Relationships | 300+ | Symptom manifestations |
| Herb-Body Part Relationships | 200+ | Target organ affinities |
| Condition-Body Part Relationships | 150+ | Affected body parts |
| Dosha-Body Part Relationships | 40+ | Governance relationships |
| Symptom-Dosha Relationships | 200+ | Diagnostic indicators |

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
├── README.md
└── DATASET_SUMMARY.md
```

## Node Features

### Herbs (205 entries)
- node_id: Unique identifier
- name: Common name
- scientific_name: Botanical name
- taste: Rasas (tastes)
- energy: Virya (potency)
- post_digestive_effect: Vipaka (post-digestive effect)
- primary_dosha_balance: Primary dosha affected
- secondary_dosha_balance: Secondary dosha affected
- properties: Therapeutic properties
- uses: Medical applications
- contraindications: Usage precautions

### Health Conditions (200+ entries)
- node_id: Unique identifier
- name: Condition name
- description: Medical description
- primary_dosha_imbalance: Primary dosha imbalance
- secondary_dosha_imbalance: Secondary dosha imbalance
- affected_body_systems: Body systems affected
- severity_level: Condition severity

### Doshas (3 entries)
- node_id: Unique identifier
- name: Dosha name (Vata, Pitta, Kapha)
- elemental_composition: Basic elements
- physical_characteristics: Physical attributes
- mental_characteristics: Mental attributes
- functions_in_body: Physiological roles
- imbalance_symptoms: Symptoms of imbalance

### Symptoms (200+ entries)
- node_id: Unique identifier
- name: Symptom name
- description: Symptom description
- associated_dosha: Related dosha
- body_location: Location in body
- severity_indicator: Severity level

### Body Parts (12 entries)
- node_id: Unique identifier
- name: Body part name
- description: Anatomical description
- primary_dosha_association: Primary governing dosha
- related_systems: Connected systems

## Edge Features

### Herb-Treats-Condition (175+ relationships)
- source_node_id: Herb ID
- target_node_id: Condition ID
- relationship_type: herb_treats_condition
- efficacy_score: Treatment effectiveness (0-1)
- strength_of_evidence: Research support level
- recommended_dosage_range: Dosage guidelines
- contraindications: Usage restrictions
- synergistic_herbs: Complementary herbs

### Herb-Balances-Dosha (200+ relationships)
- source_node_id: Herb ID
- target_node_id: Dosha ID
- relationship_type: herb_balances_dosha
- effect_type: Type of balancing effect
- intensity: Effect strength
- primary_action: Main therapeutic action
- secondary_action: Additional effects

### Condition-Aggravates-Dosha (150+ relationships)
- source_node_id: Condition ID
- target_node_id: Dosha ID
- relationship_type: condition_aggravates_dosha
- aggravation_level: Severity of aggravation
- primary_dosha: Primary dosha affected
- secondary_dosha: Secondary dosha affected
- severity_factor: Aggravation intensity

### Condition-Manifests-As-Symptom (300+ relationships)
- source_node_id: Condition ID
- target_node_id: Symptom ID
- relationship_type: condition_manifests_as_symptom
- frequency: Occurrence rate
- severity_correlation: Symptom severity relation
- primary_symptom_flag: Primary indicator status

### Herb-Targets-Body-Part (200+ relationships)
- source_node_id: Herb ID
- target_node_id: Body Part ID
- relationship_type: herb_targets_body_part
- target_specificity: Specificity of targeting
- affinity_strength: Binding strength
- mechanism_of_action: Biological mechanism

### Condition-Affects-Body-Part (150+ relationships)
- source_node_id: Condition ID
- target_node_id: Body Part ID
- relationship_type: condition_affects_body_part
- impact_severity: Severity of impact
- primary_target_flag: Primary target status
- systemic_effect: Systemic involvement

### Dosha-Governs-Body-Part (40+ relationships)
- source_node_id: Dosha ID
- target_node_id: Body Part ID
- relationship_type: dosha_governs_body_part
- governance_strength: Control intensity
- primary_governance: Primary control status
- functional_relationship: Physiological relationship

### Symptom-Indicates-Dosha-Imbalance (200+ relationships)
- source_node_id: Symptom ID
- target_node_id: Dosha ID
- relationship_type: symptom_indicates_dosha_imbalance
- indicator_strength: Diagnostic strength
- specificity: Symptom specificity
- diagnostic_value: Clinical importance

## Usage for GNN Training

This dataset can be used to train GNN models for:
1. **Herb recommendation** based on health conditions
2. **Personalized recommendations** based on dosha states
3. **Predicting herb-condition-dosha interactions**
4. **Understanding polyherbal formulations**
5. **Diagnostic assistance** based on symptom patterns
6. **Treatment pathway optimization**

The node features and edge attributes can be encoded numerically for input into GNN architectures. The heterogeneous graph structure allows for complex relationship modeling between different entity types.

## Applications

1. **Clinical Decision Support**: Assist Ayurvedic practitioners in herb selection
2. **Personalized Medicine**: Tailor treatments based on individual dosha profiles
3. **Research Tool**: Analyze herb-condition relationships systematically
4. **Educational Resource**: Teach Ayurvedic principles through data relationships
5. **Drug Discovery**: Identify potential new therapeutic applications

This comprehensive dataset provides a rich foundation for Ayurvedic herb recommendation systems using machine learning approaches, with over 500 total entries and extensive relationship mappings.