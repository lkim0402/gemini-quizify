# Quizify AI

Quizify AI is an AI-based application for generating quizzes from user-provided PDF documents. This project leverages Google Cloud's VertexAI API, LangChain, and ChromaDB to process documents, create embeddings, and generate quizzes.

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Modules](#modules)
- [License](#license)

## Features
- Process uploaded PDF documents to extract content.
- Generate embeddings for the processed documents.
- Store embeddings in ChromaDB.
- Generate quizzes based on the content of the documents.
- Manage quizzes and track the total number of questions.

##### Technologies Used
- ChromaDB: For efficient document storage and retrieval.
- LangChain: To manage and process natural language queries.
- Google Cloud Platform (GCP): Hosting and machine learning services.
- Vertex AI: AI model management and deployment.
- Streamlit: For building interactive web applications.
- Pydantic: For parsing question objects.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/lkim0402/gemini-quizify.git
   cd gemini-quizify
   ```
2. Create a virtual environment and activate it:
    ```
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
3. Install the required dependencies
    ```pip install -r requirements.txt```

## Usage
1. Start the Streamlit application:
    ```streamlit run main.py```
2. Open your web browser and navigate to `http://localhost:8501` to access the application.
3. Upload PDF documents through the Streamlit UI.
4. Specify the topic and number of quiz questions to generate.
5. The application will process the documents, generate embeddings, store them in ChromaDB, and create quiz questions based on the provided topic.

## Project Structure:
```css 
gemini-quizify/
├── DocumentProcessor.py
├── EmbeddingClient.py
├── ChromaCollectionCreator.py
├── QuizGenerator.py
├── QuizManager.py
├── main.py
├── requirements.txt
└── README.md
```

## Modules

### DocumentProcessor.py
- Processes uploaded PDF documents to extract text content.

### EmbeddingClient.py
- Converts the processed text into embeddings using VertexAI.

### ChromaCollectionCreator.py
- Stores embeddings in ChromaDB for efficient retrieval.

### QuizGenerator.py
- Generates quiz questions based on the content of the documents and provided topic.

### QuizManager.py
- Manages quiz questions, including tracking the total number of questions.

### main.py
- Ties everything together, providing the main entry point for the Streamlit application.

## Acknowledgements
This project is based on mission-quizify developed by the RadialAI Team. I thank them for providing the foundations for this project. 
