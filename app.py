import streamlit as st
import re
import nltk
from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.tree import Tree
import dateparser
import docx
import fitz  # PyMuPDF
import os

# Setup NLTK data directory for Streamlit Cloud compatibility
nltk_data_path = os.path.join(os.getcwd(), "nltk_data")
nltk.data.path.append(nltk_data_path)

def download_nltk_data():
    try:
        # Ensure all required NLTK resources are downloaded
        nltk.download('punkt', download_dir=nltk_data_path)  # Tokenizer models
        nltk.download('punkt_tab', download_dir=nltk_data_path)  # Needed for sentence tokenization
        nltk.download('maxent_ne_chunker', download_dir=nltk_data_path)  # Named Entity Chunker
        nltk.download('words', download_dir=nltk_data_path)  # Word list for named entity recognition
        nltk.download('averaged_perceptron_tagger', download_dir=nltk_data_path)  # POS tagger
    except Exception as e:
        st.error(f"Error downloading NLTK data: {e}")

download_nltk_data()

def extract_names(text):
    names = []
    try:
        # Tokenize, POS tag, and chunk named entities
        chunks = ne_chunk(pos_tag(word_tokenize(text)))
        for chunk in chunks:
            if isinstance(chunk, Tree) and chunk.label() == 'PERSON':
                name = " ".join(c[0] for c in chunk)
                names.append(name)
    except Exception as e:
        st.error(f"Error extracting names: {e}")
    return names

def extract_dates(text):
    date_regex = r'\b(?:\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}|\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4})\b'
    matches = re.findall(date_regex, text)
    parsed_dates = [dateparser.parse(match).strftime('%Y-%m-%d') for match in matches if dateparser.parse(match)]
    return parsed_dates

def read_docx(file):
    doc = docx.Document(file)
    return "\n".join([para.text for para in doc.paragraphs])

def read_pdf(file):
    pdf = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in pdf:
        text += page.get_text()
    return text

# Streamlit UI
st.title("📄 Name & Date Extractor")

input_mode = st.radio("Choose input type:", ["Upload File", "Paste Text"])

text = ""

if input_mode == "Upload File":
    uploaded_file = st.file_uploader("Upload a .txt, .docx, or .pdf file", type=['txt', 'docx', 'pdf'])
    if uploaded_file:
        if uploaded_file.type == "text/plain":
            text = uploaded_file.read().decode("utf-8")
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            text = read_docx(uploaded_file)
        elif uploaded_file.type == "application/pdf":
            text = read_pdf(uploaded_file)
        else:
            st.warning("Unsupported file type.")
elif input_mode == "Paste Text":
    text = st.text_area("Paste your text here:")

if st.button("Extract"):
    if text:
        with st.spinner("Processing..."):
            names = extract_names(text)
            dates = extract_dates(text)

        st.subheader("👤 Names Found")
        st.write(names if names else "No names found.")

        st.subheader("📅 Dates Found")
        st.write(dates if dates else "No dates found.")
    else:
        st.warning("Please enter or upload some text.")
