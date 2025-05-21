import streamlit as st
import nltk
from nltk.tokenize import word_tokenize
from nltk import pos_tag, ne_chunk
import fitz  # PyMuPDF for PDF text extraction
import io
import datefinder
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from fpdf import FPDF  # fpdf2
import os

# Download required NLTK resources
nltk.download('punkt')
nltk.download('maxent_ne_chunker')
nltk.download('words')
nltk.download('averaged_perceptron_tagger')

# Extract names
def extract_names(text):
    words = word_tokenize(text)
    tagged_words = pos_tag(words)
    named_entities = ne_chunk(tagged_words)
    names = []
    for chunk in named_entities:
        if isinstance(chunk, nltk.Tree) and chunk.label() == 'PERSON':
            name = " ".join([word for word, tag in chunk])
            names.append(name)
    return names

# Extract dates
def extract_dates(text):
    matches = datefinder.find_dates(text)
    return [match.strftime('%Y-%m-%d') for match in matches]

# Extract text from PDF
def extract_text_from_pdf(pdf_file):
    pdf_bytes = pdf_file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# Summarize using sumy
def summarize_text(text, num_sentences=3):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, num_sentences)
    return " ".join(str(sentence) for sentence in summary)

# Generate PDF report with Unicode font
def generate_pdf_report(names, dates, summary, extracted_text):
    pdf = FPDF()
    pdf.add_page()

    font_path = "FreeSerif.ttf"
    if not os.path.exists(font_path):
        raise FileNotFoundError("FreeSerif.ttf font file is missing. Please include it in the app directory.")

    pdf.add_font("FreeSerif", "", font_path, uni=True)
    pdf.set_font("FreeSerif", size=12)

    pdf.multi_cell(0, 10, "Named Entity Recognition (NER), Dates, and Summary Report\n\n")

    pdf.multi_cell(0, 10, "Extracted People Names:\n" + (", ".join(names) if names else "None") + "\n\n")
    pdf.multi_cell(0, 10, "Extracted Dates:\n" + (", ".join(dates) if dates else "None") + "\n\n")
    pdf.multi_cell(0, 10, "Summary:\n" + summary + "\n\n")
    pdf.multi_cell(0, 10, "Extracted Text:\n" + extracted_text + "\n")

    output = io.BytesIO()
    pdf.output(output)
    output.seek(0)
    return output

# Streamlit UI
st.title("NER, Date Extraction & Summarization Tool")

input_type = st.radio("Choose Input Type", ("Plain Text", "PDF File"))

if input_type == "Plain Text":
    text_input = st.text_area("Paste your text here:")
    if text_input and st.button("Extract"):
        names = extract_names(text_input)
        dates = extract_dates(text_input)
        summary = summarize_text(text_input)

        st.subheader("Extracted People Names:")
        st.write(names if names else "None found")

        st.subheader("Extracted Dates:")
        st.write(dates if dates else "None found")

        st.subheader("Summary:")
        st.write(summary)

        pdf_bytes = generate_pdf_report(names, dates, summary, text_input)
        st.download_button("Download PDF Report", data=pdf_bytes, file_name="summary_report.pdf")

elif input_type == "PDF File":
    pdf_file = st.file_uploader("Upload a PDF file", type=["pdf"])
    if pdf_file and st.button("Extract"):
        text_from_pdf = extract_text_from_pdf(pdf_file)

        st.text_area("Extracted PDF Text:", text_from_pdf)

        names = extract_names(text_from_pdf)
        dates = extract_dates(text_from_pdf)
        summary = summarize_text(text_from_pdf)

        st.subheader("Extracted People Names:")
        st.write(names if names else "None found")

        st.subheader("Extracted Dates:")
        st.write(dates if dates else "None found")

        st.subheader("Summary:")
        st.write(summary)

        pdf_bytes = generate_pdf_report(names, dates, summary, text_from_pdf)
        st.download_button("Download PDF Report", data=pdf_bytes, file_name="summary_report.pdf")
