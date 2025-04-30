import streamlit as st
from nltk import pos_tag, word_tokenize, ne_chunk
from nltk.tree import Tree
import re
import io
from PyPDF2 import PdfReader
import nltk
from nameparser import HumanName

# Ensure necessary NLTK resources are downloaded
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')

st.title("📄 Date and Name Extractor")

# Helper functions
def extract_text_from_pdf(uploaded_file):
    """Extract text from the uploaded PDF file."""
    reader = PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def extract_names(text):
    """Extract names using NLTK's Named Entity Recognition."""
    names = []
    try:
        tokens = word_tokenize(text)
        tagged = pos_tag(tokens)  # Part-of-speech tagging
        tree = ne_chunk(tagged)   # Named entity recognition
        person_list = []
        for subtree in tree:
            if isinstance(subtree, Tree) and subtree.label() == "PERSON":
                person = [leaf[0] for leaf in subtree.leaves()]
                name = ' '.join(person)
                if name not in person_list:
                    person_list.append(name)

        # Format names using HumanName
        formatted_names = []
        for name in person_list:
            human_name = HumanName(name)
            formatted_names.append(f"{human_name.last}, {human_name.first}")

        names = formatted_names

    except Exception as e:
        st.error(f"Error extracting names:\n\n{str(e)}")
    
    return names

def extract_dates(text):
    """Extract dates using a basic regex pattern."""
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
