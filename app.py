import streamlit as st
from nltk import pos_tag, word_tokenize, ne_chunk
from nltk.tree import Tree
import re
import io
import os
from PyPDF2 import PdfReader
import nltk
nltk.data.path.append('/path/to/nltk_data')  # Update with your actual path if necessary
nltk_data_path = '/root/nltk_data'  # Use a directory path where nltk data can be stored in the cloud environment

# Check if the necessary data is already downloaded
if not os.path.exists(os.path.join(nltk_data_path, 'punkt')):
    nltk.download('punkt', download_dir=nltk_data_path)
if not os.path.exists(os.path.join(nltk_data_path, 'averaged_perceptron_tagger')):
    nltk.download('averaged_perceptron_tagger', download_dir=nltk_data_path)
if not os.path.exists(os.path.join(nltk_data_path, 'maxent_ne_chunker')):
    nltk.download('maxent_ne_chunker', download_dir=nltk_data_path)
if not os.path.exists(os.path.join(nltk_data_path, 'words')):
    nltk.download('words', download_dir=nltk_data_path)

# Set the NLTK data path
nltk.data.path.append(nltk_data_path)


# Ensure necessary NLTK resources are downloaded
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')

st.title("📄 Date and Name Extractor")

# Helper functions
def extract_text_from_pdf(uploaded_file):
    reader = PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def extract_names(text):
    names = []
    try:
        # Tokenize, POS tag, and chunk using NLTK's NE chunker
        nltk_results = ne_chunk(pos_tag(word_tokenize(text)))
        for nltk_result in nltk_results:
            if isinstance(nltk_result, Tree):  # If the chunk is a tree (named entity)
                name = ''
                for nltk_result_leaf in nltk_result.leaves():
                    name += nltk_result_leaf[0] + ' '
                names.append(name.strip())  # Add the name without the trailing space
    except Exception as e:
        st.error(f"Error extracting names:\n\n{str(e)}")
    return names

def extract_dates(text):
    # Basic date pattern
    date_pattern = r"\b(?:\d{1,2}[-/th|st|nd|rd\s]*)?(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*[-/\s,]*\d{2,4}\b|\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b"
    return re.findall(date_pattern, text, flags=re.IGNORECASE)

# User input
input_mode = st.radio("Choose input method:", ["Upload PDF", "Paste Text"])

# Initialize 'text' variable
text = ""

# Depending on input method, get the text
if input_mode == "Upload PDF":
    uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])
    if uploaded_file is not None:
        text = extract_text_from_pdf(uploaded_file)
elif input_mode == "Paste Text":
    text = st.text_area("Paste your text here:")

# Extraction
if st.button("Extract"):
    if text:
        with st.spinner("Extracting..."):
            names = extract_names(text)
            dates = extract_dates(text)

        st.subheader("👤 Names Found")
        st.write(names or "No names found.")

        st.subheader("📅 Dates Found")
        st.write(dates or "No dates found.")
    else:
        st.warning("Please provide some input first.")
