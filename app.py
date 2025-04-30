import streamlit as st
import nltk
from nltk.tokenize import word_tokenize
from nltk import pos_tag, ne_chunk
import fitz  # PyMuPDF for PDF text extraction
import io  # For handling in-memory files

# Download necessary NLTK resources
nltk.download('punkt')
nltk.download('maxent_ne_chunker')
nltk.download('words')
nltk.download('averaged_perceptron_tagger')

# Function to extract names from text
def extract_names(text):
    words = word_tokenize(text)
    tagged_words = pos_tag(words)
    named_entities = ne_chunk(tagged_words)
    
    people_names = []
    for chunk in named_entities:
        if isinstance(chunk, nltk.Tree):
            if chunk.label() == 'PERSON':
                name = " ".join([word for word, tag in chunk])
                people_names.append(name)
    
    return people_names

# Function to extract text from a PDF file (now handling in-memory PDF)
def extract_text_from_pdf(pdf_file):
    # Open the PDF file from the uploaded byte stream
    pdf_bytes = pdf_file.read()  # Read the uploaded file's bytes
    doc = fitz.open(io.BytesIO(pdf_bytes))  # Using BytesIO to open the PDF from memory
    text = ""
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        page_text = page.get_text("text")
        text += page_text
    return text

# Streamlit app interface
st.title("Named Entity Recognition (NER) with NLTK")

input_type = st.radio("Choose Input Type", ("Plain Text", "PDF File"))

if input_type == "Plain Text":
    text_input = st.text_area("Paste your text here:")
    if text_input and st.button('Extract Names'):
        names = extract_names(text_input)
        if names:
            st.subheader("Extracted People Names:")
            for name in names:
                st.write(name)
        else:
            st.write("No people's names found in the text.")

elif input_type == "PDF File":
    pdf_file = st.file_uploader("Upload a PDF file", type=["pdf"])
    if pdf_file and st.button('Extract Names'):
        text_from_pdf = extract_text_from_pdf(pdf_file)
        st.text_area("Extracted PDF Text:", text_from_pdf)  # Display extracted text for debugging
        if text_from_pdf:
            names = extract_names(text_from_pdf)
            if names:
                st.subheader("Extracted People Names:")
                for name in names:
                    st.write(name)
            else:
                st.write("No people's names found in the PDF.")
        else:
            st.write("No text extracted from the PDF.")
