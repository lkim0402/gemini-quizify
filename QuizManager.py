import streamlit as st
import os
import sys
import json
sys.path.append(os.path.abspath('../../'))
from DocumentProcessor import DocumentProcessor
from EmbeddingClient import EmbeddingClient
from ChromaCollectionCreator import ChromaCollectionCreator
from QuizGenerator import QuizGenerator

class QuizManager:
    def __init__(self, questions: list):
        """
        Initializing the QuizManager class with a list of quiz questions.

        Overview:
        This task involves setting up the `QuizManager` class by initializing it with a list of quiz question objects. 
        Each quiz question object is a dictionary that includes the question text, multiple choice options, the correct answer, and an explanation. 
        The initialization process should prepare the class for managing these quiz questions, including tracking the total number of questions.

        Parameters:
        - questions: A list of dictionaries, where each dictionary represents a quiz question along with its choices, correct answer, and an explanation.

        Note: This initialization method is crucial for setting the foundation of the `QuizManager` class, enabling it to manage the quiz questions effectively. The class will rely on this setup to perform operations such as retrieving specific questions by index and navigating through the quiz.
        """
        ##### YOUR CODE HERE #####
        self.questions = questions
        self.total_questions = len(self.questions)

    def get_question_at_index(self, index: int):
        """
        Retrieves the quiz question object at the specified index. If the index is out of bounds, it restarts from the beginning index.

        :param index: The index of the question to retrieve.
        :return: The quiz question object at the specified index, with indexing wrapping around if out of bounds.
        """
        # Ensuring index is always within bounds using modulo arithmetic
        valid_index = index % self.total_questions
        return self.questions[valid_index]
    
    def next_question_index(self, direction=1):
        """
        Adjusts the current quiz question index based on the specified direction.

        Overview:
        Develop a method to navigate to the next or previous quiz question by adjusting the `question_index` in Streamlit's session state. This method should account for wrapping, meaning if advancing past the last question or moving before the first question, it should continue from the opposite end.

        Parameters:
        - direction: An integer indicating the direction to move in the quiz questions list (1 for next, -1 for previous).

        Note: Ensure that `st.session_state["question_index"]` is initialized before calling this method. This navigation method enhances the user experience by providing fluid access to quiz questions.
        """

        # Retrieving the current question index from Streamlit's session state
        current_question_index = st.session_state["question_index"]
        
        # Adjusting the index based on the provided `direction` (1 for next, -1 for previous), using modulo arithmetic to wrap around the total number of questions
        new_index = (current_question_index + direction) % self.total_questions
        
        # Updating the `question_index` in Streamlit's session state with the new, valid index.
        st.session_state["question_index"] = new_index

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

    # If question bank is generated, display the quiz
    if question_bank:
        screen.empty()
        with st.container():
            st.header("Generated Quiz Question: ")
            
            quiz_manager = QuizManager(question_bank) # Use our new QuizManager class
            with st.form("Multiple Choice Question"):
                # Using the get_question_at_index method to set the 0th index
                index_question = quiz_manager.get_question_at_index(0) 
                
                # Unpacking choices for radio
                choices = []
                for choice in index_question['choices']: # For loop to unpack the data structure
                    key = choice["key"]
                    value = choice["value"]
                    choices.append(f"{key}) {value}")
                
                # Displaying the question onto streamlit
                st.subheader(index_question['question'])
                
                # Displaying the radio button with the choices
                answer = st.radio( 
                    'Choose the correct answer',
                    choices
                )
                st.form_submit_button("Submit")
                
                if submitted: # On click submit 
                    correct_answer_key = index_question['answer']
                    if answer.startswith(correct_answer_key): # Checking if answer is correct
                        st.success("Correct!")
                    else:
                        st.error("Incorrect!")
