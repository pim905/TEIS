import streamlit as st
import nltk
from nltk.tokenize import word_tokenize
from nltk import pos_tag, ne_chunk
from nltk.tree import Tree
import fitz  # PyMuPDF
import datefinder
import os
import urllib.request
from fpdf import FPDF
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.lsa import LsaSummarizer
import re

# Download necessary NLTK resources
nltk.download('punkt')
nltk.download('maxent_ne_chunker')
nltk.download('words')
nltk.download('averaged_perceptron_tagger')

# Download FreeSerif.ttf if not present
FONT_PATH = "FreeSerif.ttf"
if not os.path.exists(FONT_PATH):
    urllib.request.urlretrieve(
        "https://ftp.gnu.org/gnu/freefont/freefont-ttf-20120503.zip",
        "freefont.zip"
    )
    import zipfile
    with zipfile.ZipFile("freefont.zip", 'r') as zip_ref:
        zip_ref.extract("FreeSerif.ttf", ".")
    os.remove("freefont.zip")

# Function to extract names
def extract_names(text):
    words = word_tokenize(text)
    tagged_words = pos_tag(words)
    named_entities = ne_chunk(tagged_words)
    people_names = []
    for chunk in named_entities:
        if isinstance(chunk, Tree) and chunk.label() == 'PERSON':
            name = " ".join([word for word, tag in chunk])
            people_names.append(name)
    return people_names

# Function to extract dates
def extract_dates(text):
    matches = datefinder.find_dates(text)
    return [match.strftime('%Y-%m-%d') for match in matches]

# Function to summarize text using sumy
def summarize_text_with_sumy(text):
    # Use the sumy PlaintextParser directly with the string text
    parser = PlaintextParser.from_string(text)
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, 3)  # Summarizes into 3 sentences (adjustable)
    return ' '.join([str(sentence) for sentence in summary])

# Clean extracted text from PDF
def clean_text(text):
    # Remove extra line breaks, spaces, and unwanted characters
    cleaned_text = re.sub(r'\n+', ' ', text)  # Replace multiple line breaks with a space
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)  # Replace multiple spaces with a single space
    cleaned_text = cleaned_text.strip()
    return cleaned_text

# Extract text from PDF
def extract_text_from_pdf(pdf_file):
    pdf_bytes = pdf_file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return clean_text(text)  # Clean the extracted text

# PDF report generation using FreeSerif.ttf
class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_font("Serif", "", FONT_PATH, uni=True)
        self.set_font("Serif", "", 12)

def generate_pdf_report(text, names, dates, summary):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Serif", "", 14)
    pdf.cell(0, 10, "Text Analysis Report", ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Serif", "", 12)
    pdf.cell(0, 10, "Extracted People Names:", ln=True)
    for name in names or ["None"]:
        pdf.cell(0, 10, f"- {name}", ln=True)

    pdf.ln(5)
    pdf.cell(0, 10, "Extracted Dates:", ln=True)
    for date in dates or ["None"]:
        pdf.cell(0, 10, f"- {date}", ln=True)

    pdf.ln(5)
    pdf.cell(0, 10, "Summary:", ln=True)
    for line in summary.split('. '):
        pdf.multi_cell(0, 10, line.strip() + '.')

    pdf.ln(5)
    pdf.cell(0, 10, "Full Text:", ln=True)
    for line in text.split('\n'):
        pdf.multi_cell(0, 10, line.strip())

    return pdf.output(dest='S').encode('utf-8')

# Streamlit UI
st.title("Named Entity & Date Extraction + PDF Summary")

input_type = st.radio("Choose Input Type", ("Plain Text", "PDF File"))

if input_type == "Plain Text":
    text_input = st.text_area("Paste your text here:")
    if text_input and st.button("Extract & Summarize"):
        names = extract_names(text_input)
        dates = extract_dates(text_input)
        summary = summarize_text_with_sumy(text_input)

        st.subheader("Extracted People Names:")
        st.write(names if names else "None found")

        st.subheader("Extracted Dates:")
        st.write(dates if dates else "None found")

        st.subheader("Summary:")
        st.write(summary)

        pdf_bytes = generate_pdf_report(text_input, names, dates, summary)
        st.download_button(
            label="📄 Download Report as PDF",
            data=pdf_bytes,
            file_name="report.pdf",
            mime="application/pdf"
        )

elif input_type == "PDF File":
    pdf_file = st.file_uploader("Upload a PDF file", type=["pdf"])
    if pdf_file and st.button("Extract & Summarize"):
        text_from_pdf = extract_text_from_pdf(pdf_file)

        st.subheader("Extracted Text:")
        st.text_area("PDF Text:", text_from_pdf, height=200)

        names = extract_names(text_from_pdf)
        dates = extract_dates(text_from_pdf)
        summary = summarize_text_with_sumy(text_from_pdf)

        st.subheader("Extracted People Names:")
        st.write(names if names else "None found")

        st.subheader("Extracted Dates:")
        st.write(dates if dates else "None found")

        st.subheader("Summary:")
        st.write(summary)

        pdf_bytes = generate_pdf_report(text_from_pdf, names, dates, summary)
        st.download_button(
            label="📄 Download Report as PDF",
            data=pdf_bytes,
            file_name="report.pdf",
            mime="application/pdf"
        )
