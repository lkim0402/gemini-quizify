import sys
import os
import streamlit as st
sys.path.append(os.path.abspath('../../'))
from DocumentProcessor import DocumentProcessor
from EmbeddingClient import EmbeddingClient


# Import Task libraries
from langchain_core.documents import Document
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.vectorstores import Chroma

class ChromaCollectionCreator:
    def __init__(self, processor, embed_model):
        """
        Initializing the ChromaCollectionCreator with a DocumentProcessor instance and embeddings configuration.
        :param processor: An instance of DocumentProcessor that has processed documents.
        :param embeddings_config: An embedding client for embedding documents.
        """
        self.processor = processor      # holds the DocumentProcessor 
        self.embed_model = embed_model  # holds the EmbeddingClient 
        self.db = None                  # holds the Chroma collection
    
    def create_chroma_collection(self):
        """
        This method creates a Chroma collection from the documents processed by the DocumentProcessor instance.
        """
        
        # Checking if any documents have been processed by the DocumentProcessor instance
        if len(self.processor.pages) == 0:
            st.error("No documents found!", icon="🚨")
            return

        # Splitting documents into text chunks suitable for embedding and indexing, using the CharacterTextSplitter from Langchain
        text_splitter = CharacterTextSplitter(
            separator="\n\n",
            chunk_size=512,
            chunk_overlap=100,
            length_function=len,
            is_separator_regex=False,
        )

        aux_array = list(map(lambda page: page.page_content, self.processor.pages))
        texts = text_splitter.create_documents(aux_array)
        
        if texts is not None:
            st.success(f"Successfully split pages to {len(texts)} documents!", icon="✅")

        # Now creating the Chroma Collection in memory with texts and the embeddings model initialized in the class
        self.db = Chroma.from_documents(
            texts, 
            self.embed_model.client, 
            persist_directory="./chroma_db")

        if self.db:
            st.success("Successfully created Chroma Collection!", icon="✅")
        else:
            st.error("Failed to create Chroma Collection!", icon="🚨")
    
    def query_chroma_collection(self, query) -> Document:
        """
        Queries the created Chroma collection for documents similar to the query.
        :param query: The query string to search for in the Chroma collection.
        
        Returns the first matching document from the collection with similarity score.
        """
        if self.db:
            docs = self.db.similarity_search_with_relevance_scores(query)
            if docs:
                return docs[0]
            else:
                st.error("No matching documents found!", icon="🚨")
        else:
            st.error("Chroma Collection has not been created!", icon="🚨")

if __name__ == "__main__":
    processor = DocumentProcessor() 
    processor.ingest_documents()
    
    embed_config = {
        "model_name": "textembedding-gecko@003",
        "project": "gemini-quizzify-427807",
        "location": "us-central1"
    }
    
    embed_client = EmbeddingClient(**embed_config) 
    
    chroma_creator = ChromaCollectionCreator(processor, embed_client)
    
    with st.form("Load Data to Chroma"):
        st.write("Select PDFs for Ingestion, then click Submit")
        
        submitted = st.form_submit_button("Submit")
        if submitted:
            chroma_creator.create_chroma_collection()