import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
import os
import tempfile
import uuid

class DocumentProcessor:
    """
    This class encapsulates the functionality for processing uploaded PDF documents using Streamlit
    and Langchain's PyPDFLoader. It provides a method to render a file uploader widget, process the
    uploaded PDF files, extract their pages, and display the total number of pages extracted.
    """
    def __init__(self):
        self.pages = []  # List to keep track of pages from all documents
    
    def ingest_documents(self):
        """
        Renders a file uploader in a Streamlit app, processes uploaded PDF files,
        extracts their pages, and updates the self.pages list with the total number of pages.
        """
        
        # Rendering a file uploader widget in Streamlit
        uploaded_files = st.file_uploader(
            type='pdf',
            accept_multiple_files=True,
            label="Upload PDF files :sunglasses:"
        )
        
        # For each uploaded PDF file:
        if uploaded_files is not None:
            for uploaded_file in uploaded_files:
                # Generating a unique identifier and append it to the original file name before saving it temporarily.
                # This avoids name conflicts and maintains traceability of the file.
                unique_id = uuid.uuid4().hex
                original_name, file_extension = os.path.splitext(uploaded_file.name)
                temp_file_name = f"{original_name}_{unique_id}{file_extension}"
                temp_file_path = os.path.join(tempfile.gettempdir(), temp_file_name)

                # Writing the content of the uploaded PDF to a temporary file.
                with open(temp_file_path, 'wb') as f:
                    f.write(uploaded_file.getvalue()) 

                # Processing the temporary file using PyPDFLoader from Langchain to load the PDF and extract pages.
                loader = PyPDFLoader(temp_file_path)
                pages_result = loader.load_and_split()                
                
                #Adding the extracted pages to the 'pages' list to keep track of the total number of pages extracted from all uploaded documents.
                for i in pages_result:
                    self.pages.append(i)
                
                # Cleaning up by deleting the temporary file after processing.
                os.unlink(temp_file_path)
            
            # Displaying the total number of pages processed.
            st.write(f"Total pages processed: {len(self.pages)}")
        
if __name__ == "__main__":
    processor = DocumentProcessor()
    processor.ingest_documents()
