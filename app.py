import streamlit as st
import nltk
from nltk.tokenize import word_tokenize
from nltk import pos_tag, ne_chunk
import pdfplumber
import io
import datefinder

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from fpdf import FPDF  # PDF generation

# Download necessary NLTK resources
nltk.download('punkt')
nltk.download('maxent_ne_chunker')
nltk.download('words')
nltk.download('averaged_perceptron_tagger')

# Extract names from text
def extract_names(text):
    words = word_tokenize(text)
    tagged_words = pos_tag(words)
    named_entities = ne_chunk(tagged_words)
    
    people_names = []
    for chunk in named_entities:
        if isinstance(chunk, nltk.Tree) and chunk.label() == 'PERSON':
            name = " ".join([word for word, tag in chunk])
            people_names.append(name)
    return people_names

# Extract dates from text
def extract_dates(text):
    matches = datefinder.find_dates(text)
    dates = [match.strftime('%Y-%m-%d') for match in matches]
    return dates

# Extract text from PDF using pdfplumber
def extract_text_from_pdf(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

# Summarize text
def summarize_text(text, num_sentences=3):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, num_sentences)
    summarized_text = " ".join(str(sentence) for sentence in summary)
    return summarized_text

# Generate PDF report
def generate_pdf_report(names, dates, summary, extracted_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="Extracted Information Report", ln=True, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", size=12)

    def safe_text(text):
        return text.encode('latin-1', 'replace').decode('latin-1')

    pdf.multi_cell(0, 10, safe_text(f"Extracted Text:\n{extracted_text}\n\n"))

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Extracted People Names:", ln=True)
    pdf.set_font("Arial", size=12)
    for name in names:
        pdf.cell(200, 10, txt=safe_text(f"- {name}"), ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Extracted Dates:", ln=True)
    pdf.set_font("Arial", size=12)
    for date in dates:
        pdf.cell(200, 10, txt=f"- {date}", ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="Summary:", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, safe_text(summary))

    pdf_output = pdf.output(dest='S').encode('latin-1')
    return pdf_output

# Streamlit UI
st.title("Named Entity Recognition (NER), Date Extraction, and Text Summarization")

input_type = st.radio("Choose Input Type", ("Plain Text", "PDF File"))

if input_type == "Plain Text":
    text_input = st.text_area("Paste your text here:")
    if text_input and st.button('Extract Names, Dates, and Summary'):
        names = extract_names(text_input)
        dates = extract_dates(text_input)
        summary = summarize_text(text_input)

        if names:
            st.subheader("Extracted People Names:")
            for name in names:
                st.write(name)
        else:
            st.write("No people's names found in the text.")

        if dates:
            st.subheader("Extracted Dates:")
            for date in dates:
                st.write(date)
        else:
            st.write("No dates found in the text.")

        if summary:
            st.subheader("Summary of the Text:")
            st.write(summary)

        pdf_bytes = generate_pdf_report(names, dates, summary, text_input)
        st.download_button("Download PDF Report", data=pdf_bytes, file_name="extracted_report.pdf", mime="application/pdf")

elif input_type == "PDF File":
    pdf_file = st.file_uploader("Upload a PDF file", type=["pdf"])
    if pdf_file and st.button('Extract Names, Dates, and Summary'):
        text_from_pdf = extract_text_from_pdf(pdf_file)
        st.text_area("Extracted PDF Text:", text_from_pdf)

        if text_from_pdf:
            names = extract_names(text_from_pdf)
            dates = extract_dates(text_from_pdf)
            summary = summarize_text(text_from_pdf)

            if names:
                st.subheader("Extracted People Names:")
                for name in names:
                    st.write(name)
            else:
                st.write("No people's names found in the PDF.")

            if dates:
                st.subheader("Extracted Dates:")
                for date in dates:
                    st.write(date)
            else:
                st.write("No dates found in the PDF.")

            if summary:
                st.subheader("Summary of the PDF Text:")
                st.write(summary)

            pdf_bytes = generate_pdf_report(names, dates, summary, text_from_pdf)
            st.download_button("Download PDF Report", data=pdf_bytes, file_name="extracted_report.pdf", mime="application/pdf")
        else:
            st.write("No text extracted from the PDF.")
