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
- Processes uploaded PDF documents to ingest text content using LangChain's PyPDFLoader. Processes the uploaded PDF files, extract their pages, and get the total number of extracted pages.
- For each uploaded PDF file, it generates a unique identifier and appends it to the original file name before saving to avoid name conflict.

### EmbeddingClient.py
- Converts the processed text into embeddings using VertexAIEmbeddings API from GCP.
- Functions include `embed_query` to retrieve embeddings for the given query, and `embed_documents` to retrieve embeddings for multiple documents.


### ChromaCollectionCreator.py
- Stores embeddings in ChromaDB for efficient retrieval. Utilizes the DocumentProcessor class and the EmbeddingClient class. 
- Functions include
    - `create_chroma_collection`: Creates a ChromaDB collection from the documents processed by the DocumentProcessor
    - `query_chroma_collection`: Queries the created chroma collection for documents similar to the query. Returns the first matching document from the collection with similarity score.

### QuizGenerator.py
- Generates quiz questions based on the content of the documents and provided topic.
- Utilized Pydantic's BaseModel to create a schema for the question object.
- The functions of the QuizGenerator class include
    - `init_llm`: Initializes and configures the Large Language Model (LLM) for generating quiz questions. Utilized `VertexAI` from `langchain_google_vertexai`.
    - `generate_question_with_vectorstore`: Generates a quiz question based on the topic provided and context using a vectorstore
    - `validate_question`: Validates a quiz question for uniqueness within the generated quiz
    - `generate_quiz`: Generates a list of unique quiz questions based on the specified topic and number of questions.
        - Utilizes the `generate_question_with_vectorstore` method to generate each question and the `validate_question` method to ensure its uniqueness before adding it to the quiz.
        - Returns a list of dictionaries, where each dictionary represents a unique quiz question

### QuizManager.py
- Manages quiz questions, including tracking the total number of questions.
- Functions include
    - `get_question_at_index`: Retrieves the quiz question object at the specified index
    - `next_question_index`: Adjusts the current quiz question index based on the specified direction

### main.py
- Ties everything together, providing the main entry point for the Streamlit application.

## Acknowledgements
This project is based on mission-quizify developed by the RadialAI Team. I thank them for providing the foundations for this project. 
