import streamlit as st
import os
import sys
import json
sys.path.append(os.path.abspath('../../'))
from DocumentProcessor import DocumentProcessor
from EmbeddingClient import EmbeddingClient
from ChromaCollectionCreator import ChromaCollectionCreator

from langchain_core.prompts import PromptTemplate
from langchain_google_vertexai import VertexAI

from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List


# Creating a schema for the question object
class Choice(BaseModel):
    key: str = Field(description="The key for the choice, should be one of 'A', 'B', 'C', or 'D'.")
    value: str = Field(description="The text of the choice.")

class QuestionSchema(BaseModel):
    question: str = Field(description="The text of the question.")
    choices: List[Choice] = Field(description="A list of choices for the question, each with a key and a value.")
    answer: str = Field(description="The key of the correct answer from the choices list.")
    explanation: str = Field(description="An explanation as to why the answer is correct.")

    model_config = {
        "json_schema_extra": {
            "examples": """ 
                {
                "question": "What is the capital of France?",
                "choices": [
                    {"key": "A", "value": "Berlin"},
                    {"key": "B", "value": "Madrid"},
                    {"key": "C", "value": "Paris"},
                    {"key": "D", "value": "Rome"}
                ],
                "answer": "C",
                "explanation": "Paris is the capital of France."
              }
          """
        }
      }

# Building the QuizGenerator class
class QuizGenerator:
    def __init__(self, topic=None, num_questions=1, vectorstore=None):
        """
        Initializes the QuizGenerator with a required topic, the number of questions, and an optional vectorstore for querying related information.

        :param topic: A string representing the required topic of the quiz.
        :param num_questions: An integer representing the number of questions to generate for the quiz, up to a maximum of 10.
        :param vectorstore: An optional vectorstore instance (e.g., ChromaDB) to be used for querying information related to the quiz topic.
        """
        
        if not topic:
            self.topic = "General Knowledge"
        else:
            self.topic = topic

        if num_questions > 10:
            raise ValueError("Number of questions cannot exceed 10.")
        
        self.num_questions = num_questions
        self.vectorstore = vectorstore
        self.llm = None
        
        # Initialize the JsonOutputParser with the QuestionSchema
        # JsonOutputParser: a utility class used to parse JSON output from a language model (LLM) and ensure that the output conforms to a specific schema
        self.parser = JsonOutputParser(pydantic_object=QuestionSchema)
        
        # Initialize the question bank to store questions
        self.question_bank = [] 
        self.system_template = """
            You are a subject matter expert on the topic: {topic}
            
            Follow the instructions to create a quiz question:
            1. Generate a question based on the topic provided and context as key "question"
            2. Provide 4 multiple choice answers to the question as a list of key-value pairs "choices"
            3. Provide the correct answer for the question from the list of answers as key "answer"
            4. Provide an explanation as to why the answer is correct as key "explanation"
            
            {format_instructions}
            
            Context: {context}
            """
    
    def init_llm(self):
        """
        Initializes and configures the Large Language Model (LLM) for generating quiz questions.

        This method should handle any setup required to interact with the LLM, including authentication,
        setting up any necessary parameters, or selecting a specific model.

        :return: An instance or configuration for the LLM.
        """
        self.llm = VertexAI(
            model_name = "gemini-pro",
            temperature = 0.8, # Increased for less deterministic questions 
            max_output_tokens = 500
        )

    def generate_question_with_vectorstore(self):
        """
        Generates a quiz question based on the topic provided and context using a vectorstore

        Overview:
        This method leverages the vectorstore to retrieve relevant context for the quiz topic, then utilizes the LLM to generate a structured quiz question in JSON format. 
        The process involves retrieving documents, creating a prompt, and invoking the LLM to generate a question.

        :return: A JSON object representing the generated quiz question.
        """
        if not self.llm:
            self.init_llm()
        if not self.vectorstore:
            raise ValueError("Vectorstore not provided.")
        
        from langchain_core.runnables import RunnablePassthrough, RunnableParallel

        # Enable a Retriever: get relevant documents from the vectorstore
        retriever = self.vectorstore.db.as_retriever()
        
        # Use the system template to create a PromptTemplate
        prompt = PromptTemplate(
            template = self.system_template,
            input_variables=["topic", "context"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()},
        )
        
        # RunnableParallel allows Retriever to get relevant documents
        # RunnablePassthrough allows chain.invoke to send self.topic to LLM
        setup_and_retrieval = RunnableParallel(
            {"context": retriever, "topic": RunnablePassthrough()}
        )
        # Creating a chain with the Retriever, PromptTemplate, and LLM
        chain = setup_and_retrieval | prompt | self.llm | self.parser
        """
        The chain is constructed as follows:
            1. setup_and_retrieval: Retrieves relevant documents from the vectorstore and passes them to the next step.
            2. prompt: Creates a prompt template using the system template and the retrieved documents.
            3. self.llm: Generates the quiz question based on the formatted prompt.
            4. self.parser: Parses the output from the LLM to ensure it conforms to the QuestionSchema.
        Output: A validated and structured quiz question in JSON format.
        """
        response = chain.invoke(self.topic)
        return response


    def validate_question(self, question: dict) -> bool:
        """
        Validates a quiz question for uniqueness within the generated quiz.
        Checks if the provided question (as a dictionary) is unique based on its text content compared to previously generated questions stored in `question_bank`. 
        The goal is to ensure that no duplicate questions are added to the quiz.

        Parameters:
        - question: A dictionary representing the generated quiz question, expected to contain at least a "question" key.

        Returns:
        - A boolean value: True if the question is unique, False otherwise.

        Note: This method assumes `question` is a valid dictionary and `question_bank` has been properly initialized.
        """
        # Consider missing 'question' key as invalid in the dict object
        if 'question' not in question or not question['question']:
            raise ValueError("The dict object must contain a non-empty 'question' key")

        # Check if a question with the same text already exists in the self.question_bank
        is_unique = True

        # Iterating over the existing questions in `question_bank` and compare their texts to the current question's text
        for question_iterated in self.question_bank:
            if(question_iterated['question'] == question['question']):
                is_unique = False
                break

        return is_unique
    
    
    def generate_quiz(self) -> list:
        """
        Generates a list of unique quiz questions based on the specified topic and number of questions.
        Utilizes the `generate_question_with_vectorstore` method to generate each question and the `validate_question` method to ensure its uniqueness before adding it to the quiz.

        Returns:
        - A list of dictionaries, where each dictionary represents a unique quiz question generated based on the topic.

        Note: This method relies on `generate_question_with_vectorstore` for question generation and `validate_question` for ensuring question uniqueness. 
        Ensure `question_bank` is properly initialized and managed.
        """
        
        # Initializing an empty list to store the unique quiz questions
        self.question_bank = [] # Resetting the question bank

        for _ in range(self.num_questions):
            # Generating a question
            question = self.generate_question_with_vectorstore()
            
            # Validatig the question's uniqueness using the validate_question method
            if self.validate_question(question):
                print("Successfully generated unique question")
                # If valid and unique, add it to the bank
                self.question_bank.append(question)
                
            else:
                print("Duplicate or invalid question detected.")

                for i in range(3): #Retry limit of 3 attempts
                    question_str = self.generate_question_with_vectorstore()
                    
                    try:
                        question = json.loads(question_str)
                    except json.JSONDecodeError:
                        print("Failed to decode question JSON.")
                        continue 
                    
                    if self.validate_question(question):
                        print("Successfully generated unique question")
                        self.question_bank.append(question)
                        break
                    else:
                        print("Duplicate or invalid question detected - Attempt "+(i+1))
                        continue

        return self.question_bank


# Test Generating the Quiz
if __name__ == "__main__":
    
    embed_config = {
        "model_name": "textembedding-gecko@003",
        "project": "gemini-quizzify-427807",
        "location": "us-central1"
    }
    
    screen = st.empty()
    with screen.container():
        st.header("Quiz Builder")
        processor = DocumentProcessor()
        processor.ingest_documents()
    
        embed_client = EmbeddingClient(**embed_config) 
    
        chroma_creator = ChromaCollectionCreator(processor, embed_client)
    
        question = None
        question_bank = None
    
        with st.form("Load Data to Chroma"):
            st.subheader("Quiz Builder")
            st.write("Select PDFs for Ingestion, the topic for the quiz, and click Generate!")
            
            topic_input = st.text_input("Topic for Generative Quiz", placeholder="Enter the topic of the document")
            questions = st.slider("Number of Questions", min_value=1, max_value=10, value=1)
            
            submitted = st.form_submit_button("Submit")
            if submitted:
                chroma_creator.create_chroma_collection()
                
                st.write(topic_input)
                
                # Test the Quiz Generator
                generator = QuizGenerator(topic_input, questions, chroma_creator)
                question_bank = generator.generate_quiz()
                question = question_bank[0]

    if question_bank:
        screen.empty()
        with st.container():
            st.header("Generated Quiz Question: ")
            for question in question_bank:
                st.write(question)













