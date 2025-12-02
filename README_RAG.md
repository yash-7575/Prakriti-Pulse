# RAG Chatbot with Gemini Integration

This project now supports Retrieval-Augmented Generation (RAG) using Google's Gemini API.

## Features

- **Gemini Integration**: Uses Google's Gemini Pro for intelligent responses and embeddings.
- **Custom Data**: You can train the chatbot with your own data by adding it to `rag_data.txt`.
- **Hybrid Search**: Falls back to TF-IDF if Gemini is unavailable.

## Setup

1.  **API Key**:
    -   Open `.env` file.
    -   Add your Gemini API key: `GEMINI_API_KEY=your_actual_api_key_here`.

2.  **Add Data**:
    -   Open `rag_data.txt`.
    -   Paste your text data. Separate different sections with double newlines.
    -   The chatbot will automatically load this data on startup.

3.  **Run**:
    -   Start the application normally: `python app.py`.

## Troubleshooting

-   If you see "Gemini API not configured", check your `.env` file.
-   If the chatbot returns generic answers, ensure your `rag_data.txt` contains relevant information.
