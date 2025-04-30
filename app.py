import spacy
import streamlit as st
from datetime import datetime
import spacy.cli
import os

# Check if the spaCy model is already installed; if not, download it
if not os.path.exists(spacy.util.get_package_path("en_core_web_trf")):
    spacy.cli.download("en_core_web_trf")

# Load the spaCy model for Named Entity Recognition (NER)
nlp = spacy.load("en_core_web_trf")

# Function to extract names and dates from text using spaCy
def extract_names_and_dates(text):
    doc = nlp(text)

    # Initialize empty lists to store names and dates
    names = []
    dates = []

    # Loop through the named entities identified by spaCy
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            names.append(ent.text)  # Extract names
        elif ent.label_ == "DATE":
            # You can normalize dates if needed (optional)
            try:
                parsed_date = datetime.strptime(ent.text, '%Y-%m-%d')
                dates.append(parsed_date.strftime('%B %d, %Y'))
            except ValueError:
                dates.append(ent.text)  # If date is in a non-standard format

    return names, dates

# Streamlit app code
st.set_page_config(page_title="Name and Date Extractor", layout="centered")
st.title("📄 Extract Names & Dates from Documents")

st.markdown("Upload a document and this app will extract people's names and dates.")

# File uploader
uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx", "txt"])

def read_file(file):
    if file.name.endswith(".pdf"):
        # Handle PDF reading (can use PyPDF2 or other libraries)
        pass
    elif file.name.endswith(".docx"):
        # Handle DOCX reading (use python-docx)
        pass
    elif file.name.endswith(".txt"):
        # Handle TXT reading
        text = file.read().decode("utf-8")
        return text
    return ""

if uploaded_file:
    # Read the uploaded file
    text = read_file(uploaded_file)

    if text:
        # Display the raw text
        st.subheader("Extracted Text")
        st.text_area("Raw Text", text, height=200)

        # Extract names and dates using spaCy
        names, dates = extract_names_and_dates(text)

        # Show the results
        st.subheader("Extracted Names and Dates")
        st.write("Names:", names)
        st.write("Dates:", dates)
    else:
        st.warning("No text extracted from file.")
