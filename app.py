import streamlit as st
from nltk.tree import Tree
from nltk import word_tokenize, pos_tag
import re
import io
from PyPDF2 import PdfReader
import nltk
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
        tokens = word_tokenize(text)
        tagged = pos_tag(tokens, lang='eng')  # Use correct lang code
        tree = ne_chunk(tagged)
        for chunk in tree:
            if isinstance(chunk, Tree) and chunk.label() == "PERSON":
                name = " ".join(c[0] for c in chunk)
                names.append(name)
    except Exception as e:
        st.error(f"Error extracting names:\n\n{str(e)}")
    return names

def extract_dates(text):
    # Very basic pattern, can be expanded
    date_pattern = r"\b(?:\d{1,2}[-/th|st|nd|rd\s]*)?(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*[-/\s,]*\d{2,4}\b|\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b"
    return re.findall(date_pattern, text, flags=re.IGNORECASE)

# User input
input_mode = st.radio("Choose input method:", ["Upload PDF", "Paste Text"])

text = ""
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
