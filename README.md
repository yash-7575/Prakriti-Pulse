# 🌿 Prakriti Pulse: Advanced Ayurvedic Healthcare Intelligence

**Prakriti Pulse** is a state-of-the-art Ayurvedic health platform that leverages **Graph Neural Networks (GNN)**, **Artificial Intelligence**, and **Knowledge Graphs** to provide personalized herb recommendations and clinical guidance. By analyzing a patient's **Prakriti** (body constitution) and current symptoms, the system bridges ancient Ayurvedic wisdom with modern machine learning.

---

## 🚀 Key Features

### 🧠 1. AI-Powered Recommendation Engine
*   **Heterogeneous Graph Neural Network (GNN)**: Uses a custom-trained `HeteroGNN` (built with PyTorch Geometric) to predict the most effective herbs for specific symptoms.
*   **Dynamic Matching**: Computes match scores based on complex relationships between Herbs, Doshas, Conditions, and Symptoms.
*   **Fallback Logic**: Seamlessly switches to rule-based graph queries if AI inference is unavailable.

### 💬 2. Hybrid RAG Chatbot
*   **Retrieval-Augmented Generation (RAG)**: Integrates with Google Gemini AI to provide context-aware answers using a curated Ayurvedic knowledge base.
*   **Reinforcement Learning (RL)**: Employs contextual bandits to "learn" whether a user prefers detailed RAG responses or concise rule-based answers based on feedback.
*   **Dosha-Aware Intelligence**: The chatbot considers the user's current Prakriti and symptoms when generating advice.

### 🕸️ 3. Extensive Knowledge Graph
*   **Neo4j Backend**: Stores thousands of nodes and relationships including:
    *   **Nodes**: Herbs, Symptoms, Doshas (Vata, Pitta, Kapha), Conditions, Gunas, Rasas, etc.
    *   **Edges**: `TREATS`, `BALANCES`, `AGGRAVATES`, `MANIFESTS_AS`, `HAS_RASA`, etc.
*   **ETL Pipeline**: Automated scripts to load and normalize Ayurvedic data from CSV sources into the graph.

---

## 🛠️ Tech Stack

- **Backend**: Python 3.x, Flask
- **Database**: Neo4j (GraphDB)
- **AI/ML Frameworks**: 
    - PyTorch & PyTorch Geometric (GNN Inference)
    - scikit-learn (TF-IDF Vectorization)
    - Google Generative AI (Gemini Flash 2.0/2.5)
- **Frontend**: HTML5, CSS3 (Modern Glassmorphism UI), Vanilla JavaScript
- **Integration**: RAG, Contextual Bandits (RL), Custom ETL

---

## 📂 Project Structure

```text
├── ai_engine/          # GNN Model artifacts (.pth, .pt, mappings.pkl) and inference logic
├── nodes/              # CSV data for Knowledge Graph nodes (Herbs, Symptoms, etc.)
├── edges/              # CSV data for Knowledge Graph relationships
├── static/             # CSS styling, JS interactions, and image assets
├── templates/          # Jinja2 HTML templates for the web interface
├── app.py              # Main Flask application & API routes
├── chatbot_service.py  # RAG logic & Gemini AI integration
├── database_config.py  # Neo4j connection and Cypher query layer
├── etl_loader.py       # Knowledge Graph builder (CSV -> Neo4j)
├── rl_service.py       # Reinforcement Learning for chatbot strategy
└── requirements.txt    # Python dependencies
```

---

## ⚙️ Installation & Setup

### 1. Prerequisites
- python 3.9+
- Neo4j Desktop (with a database named `ayurveda` and password `ayurveda_password`)
- Gemini API Key (if using RAG features)

### 2. Clone and Install
```bash
git clone https://github.com/yash-7575/Prakriti-Pulse.git
cd Prakriti-Pulse
pip install -r requirements.txt
```

### 3. Database Initialization
Ensure Neo4j is running, then run the ETL loader:
```bash
python etl_loader.py
```

### 4. Configure Environment
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_actual_api_key_here
```

### 5. Run the Application
```bash
python app.py
```
Visit `http://localhost:5000` in your browser.

---

## 🧠 How it Works

1.  **Patient Registration**: Users enter their profile details and determine their Prakriti type.
2.  **Symptom Entry**: Users select current health concerns from an extensive symptoms database.
3.  **Inference**:
    - The **AI Engine** runs the symptoms through the HeteroGNN to find herb embeddings with high "Match Scores".
    - Simultaneously, **Neo4j** performs a pathfinding query to find herbs traditionally used for those symptoms.
4.  **Interaction**: The user can chat with the **Prakriti Pulse Assistant**, which uses RAG to pull specific dosage and contraindication info directly from the graph data.

---

## 📜 Disclaimer
*Prakriti Pulse is an AI-driven educational tool. It is not a replacement for professional medical advice, diagnosis, or treatment. Always seek the advice of a qualified Ayurvedic practitioner or physician.*
