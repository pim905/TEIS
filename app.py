import streamlit as st
import nltk
import re
import io
import PyPDF2
from nltk import ne_chunk, pos_tag, word_tokenize
from nltk.tree import Tree

# Ensure required NLTK data is downloaded
nltk_data_path = './nltk_data'
nltk.download('punkt', download_dir=nltk_data_path)
nltk.download('averaged_perceptron_tagger', download_dir=nltk_data_path)
nltk.download('maxent_ne_chunker', download_dir=nltk_data_path)
nltk.download('words', download_dir=nltk_data_path)

nltk.data.path.append(nltk_data_path)


def extract_names(text):
    names = []
    try:
        tokens = word_tokenize(text)
        tagged = pos_tag(tokens)
        chunks = ne_chunk(tagged)
        for chunk in chunks:
            if isinstance(chunk, Tree) and chunk.label() == 'PERSON':
                name = " ".join(c[0] for c in chunk)
                names.append(name)
    except Exception as e:
        st.error(f"Error extracting names:\n\n{e}")
    return list(set(names))


def extract_dates(text):
    # Simple regex for common date formats
    date_patterns = [
        r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',        # 12/31/2020 or 12-31-2020
        r'\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',          # 2020-12-31
        r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},\s+\d{4}\b',  # Dec 31, 2020
        r'\b\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b',  # 31 December 2020
    ]
    dates = []
    for pattern in date_patterns:
        dates.extend(re.findall(pattern, text, re.IGNORECASE))
    return list(set(dates))


def read_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text


st.title("📄 Text & PDF Name/Date Extractor")

input_type = st.radio("Choose input type:", ("Upload File", "Paste Text"))

text = ""

if input_type == "Upload File":
    uploaded_file = st.file_uploader("Upload a .txt or .pdf file", type=["txt", "pdf"])
    if uploaded_file:
        if uploaded_file.type == "application/pdf":
            text = read_pdf(uploaded_file)
        elif uploaded_file.type == "text/plain":
            stringio = io.StringIO(uploaded_file.getvalue().decode("utf-8"))
            text = stringio.read()
        else:
            st.error("Unsupported file type.")
else:
    text = st.text_area("Paste your text here:")

if st.button("Extract"):
    if text.strip():
        with st.spinner("Extracting..."):
            names = extract_names(text)
            dates = extract_dates(text)

        st.subheader("👤 Names Found")
        st.write(names if names else "No names found.")

        st.subheader("📅 Dates Found")
        st.write(dates if dates else "No dates found.")
    else:
        st.warning("Please upload a file or paste some text.")
