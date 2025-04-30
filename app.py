import streamlit as st
import spacy
from io import StringIO

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# Function to extract names and dates from text
def extract_entities(text):
    doc = nlp(text)
    names = []
    dates = []
    
    # Extracting names (PERSON) and dates (DATE)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            names.append(ent.text)
        elif ent.label_ == "DATE":
            dates.append(ent.text)
    
    return names, dates

# Streamlit interface
st.title("Entity Extractor (Names and Dates)")

# Option for user to choose between document upload and plain text input
option = st.selectbox("Choose input type", ("Upload Document", "Enter Plain Text"))

if option == "Upload Document":
    uploaded_file = st.file_uploader("Choose a document", type=["txt", "pdf", "docx"])
    if uploaded_file is not None:
        # Read the content of the document
        if uploaded_file.type == "text/plain":
            text = uploaded_file.getvalue().decode("utf-8")
        elif uploaded_file.type == "application/pdf":
            # For PDF files, you can use PyMuPDF or pdfplumber (install them if needed)
            import pdfplumber
            with pdfplumber.open(uploaded_file) as pdf:
                text = "\n".join([page.extract_text() for page in pdf.pages])
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            # For DOCX files, you can use python-docx
            from docx import Document
            doc = Document(uploaded_file)
            text = "\n".join([p.text for p in doc.paragraphs])
        
        # Extract names and dates
        names, dates = extract_entities(text)
        
        # Display extracted entities
        st.subheader("Extracted Names")
        st.write(names)
        
        st.subheader("Extracted Dates")
        st.write(dates)

elif option == "Enter Plain Text":
    input_text = st.text_area("Enter your text here")
    if input_text:
        # Extract names and dates
        names, dates = extract_entities(input_text)
        
        # Display extracted entities
        st.subheader("Extracted Names")
        st.write(names)
        
        st.subheader("Extracted Dates")
        st.write(dates)
