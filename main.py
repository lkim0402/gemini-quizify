import streamlit as st
import os
import sys
import json
sys.path.append(os.path.abspath('../../'))
from DocumentProcessor import DocumentProcessor
from EmbeddingClient import EmbeddingClient
from ChromaCollectionCreator import ChromaCollectionCreator
from QuizGenerator import QuizGenerator
from QuizManager import QuizManager


if __name__ == "__main__":
    
    embed_config = {
        "model_name": "textembedding-gecko@003",
        "project": "gemini-quizzify-427807",
        "location": "us-central1"
    }
    
    
    
    # Add Session State
    if "question_bank" not in st.session_state or len(st.session_state["question_bank"]) == 0:
        
        # Initializing the question bank list in st.session_state
        st.session_state["question_bank"] = []
    
        screen = st.empty()
        with screen.container():
            st.header("Quiz Builder")
            
            # Creating aa new st.form flow control for Data Ingestion
            with st.form("Load Data to Chroma"):
                st.write("Select PDFs for Ingestion, the topic for the quiz, and click Generate!")
                
                processor = DocumentProcessor()
                processor.ingest_documents()
            
                embed_client = EmbeddingClient(**embed_config) 
            
                chroma_creator = ChromaCollectionCreator(processor, embed_client)
                
                # Setting topic input and number of questions
                topic_input = st.text_input("Topic for Generative Quiz", placeholder="Enter the topic of the document")
                questions = st.slider("Number of Questions", min_value=1, max_value=10, value=1)

                # Submit button                    
                submitted = st.form_submit_button("Submit")
                
                if submitted:
                    chroma_creator.create_chroma_collection()
                        
                    if len(processor.pages) > 0:
                        st.write(f"Generating {questions} questions for topic: {topic_input}")
                    
                    # Initializing a QuizGenerator class using the topic, number of questrions, and the chroma collection
                    generator = QuizGenerator(topic_input, questions, chroma_creator) 
                    question_bank = generator.generate_quiz() #getting the question bank
                    
                    # Initializing the question bank list in st.session_state
                    st.session_state["question_bank"] = question_bank

                    # Setting a display_quiz flag in st.session_state to True
                    if "display_quiz" not in st.session_state:
                        st.session_state["display_quiz"] = True
                                    
                    # Setting the question_index to 0 in st.session_state
                    if "question_index" not in st.session_state:
                        st.session_state["question_index"] = 0

                    st.rerun()


    elif st.session_state["display_quiz"]:

        question_bank = st.session_state["question_bank"]

        st.empty()
        with st.container():
            st.header("Generated Quiz Question: ")
            quiz_manager = QuizManager(question_bank)
                
            # Format the question and display it
            with st.form("MCQ"):
                # Setting index_question using the Quiz Manager method get_question_at_index passing the st.session_state["question_index"]
                index_question = quiz_manager.get_question_at_index(st.session_state["question_index"])                   

                # Unpacking choices for radio button
                choices = []
                for choice in index_question['choices']:
                    key = choice['key']
                    value = choice['value']
                    choices.append(f"{key}) {value}")
                    
                 # Display the Question
                st.write(f"{st.session_state['question_index'] + 1}. {index_question['question']}")
                answer = st.radio(
                    "Choose an answer",
                    choices,
                    index = None
                )
                    
                answer_choice = st.form_submit_button("Submit")
                    
                ##### YOUR CODE HERE #####
                # Adding Buttons to navigate to the next and previous questions
                st.form_submit_button("Next Question", on_click=lambda: quiz_manager.next_question_index(direction=1))
                st.form_submit_button("Previous Question", on_click=lambda: quiz_manager.next_question_index(direction=-1))
                    
                if answer_choice and answer is not None:
                    correct_answer_key = index_question['answer']
                    if answer.startswith(correct_answer_key):
                        st.success("Correct!")
                    else:
                        st.error("Incorrect!")
                    st.write(f"Explanation: {index_question['explanation']}")