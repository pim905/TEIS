import streamlit as st
import nltk
from nltk.tokenize import word_tokenize
from nltk import pos_tag, ne_chunk
import fitz  # PyMuPDF for PDF text extraction
import datefinder  # For extracting dates from text
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from fpdf import FPDF

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
        if isinstance(chunk, nltk.Tree) and chunk.label() == 'PERSON':
            name = " ".join([word for word, tag in chunk])
            people_names.append(name)
    
    return people_names

# Function to extract dates from text
def extract_dates(text):
    matches = datefinder.find_dates(text)
    dates = [match.strftime('%Y-%m-%d') for match in matches]
    return dates

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    pdf_bytes = pdf_file.read()
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    text = ""
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text += page.get_text("text")
    return text

# Function to summarize text
def summarize_text(text, num_sentences=3):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, num_sentences)
    return " ".join(str(sentence) for sentence in summary)

# Function to generate PDF report
def generate_pdf_report(text, names, dates, summary):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Text Analysis Report", ln=True, align="C")

    pdf.set_font("Arial", '', 12)
    pdf.ln(10)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Extracted People Names:", ln=True)
    pdf.set_font("Arial", '', 12)
    if names:
        for name in names:
            pdf.cell(0, 10, f"- {name}", ln=True)
    else:
        pdf.cell(0, 10, "None", ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Extracted Dates:", ln=True)
    pdf.set_font("Arial", '', 12)
    if dates:
        for date in dates:
            pdf.cell(0, 10, f"- {date}", ln=True)
    else:
        pdf.cell(0, 10, "None", ln=True)

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Summary:", ln=True)
    pdf.set_font("Arial", '', 12)
    for line in summary.split('. '):
        pdf.multi_cell(0, 10, line.strip() + '.')

    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Full Text:", ln=True)
    pdf.set_font("Arial", '', 12)
    for line in text.split('\n'):
        pdf.multi_cell(0, 10, line.strip())

    pdf_output = pdf.output(dest='S').encode('latin-1')
    return pdf_output

# Streamlit app
st.title("🧠 Text Analysis: NER, Dates, Summary & PDF Report")

input_type = st.radio("Choose Input Type", ("Plain Text", "PDF File"))

if input_type == "Plain Text":
    text_input = st.text_area("Paste your text here:")
    if text_input and st.button('Extract Names, Dates, and Summary'):
        names = extract_names(text_input)
        dates = extract_dates(text_input)
        summary = summarize_text(text_input)

        if names:
            st.subheader("🧑 Extracted People Names:")
            for name in names:
                st.write(name)
        else:
            st.write("No people's names found.")

        if dates:
            st.subheader("📅 Extracted Dates:")
            for date in dates:
                st.write(date)
        else:
            st.write("No dates found.")

        if summary:
            st.subheader("📝 Summary:")
            st.write(summary)

        # PDF download
        pdf_bytes = generate_pdf_report(text_input, names, dates, summary)
        st.download_button(
            label="📄 Download Report as PDF",
            data=pdf_bytes,
            file_name="text_analysis_report.pdf",
            mime="application/pdf"
        )

elif input_type == "PDF File":
    pdf_file = st.file_uploader("Upload a PDF file", type=["pdf"])
    if pdf_file and st.button('Extract Names, Dates, and Summary'):
        text_from_pdf = extract_text_from_pdf(pdf_file)
        st.text_area("Extracted PDF Text:", text_from_pdf, height=200)

        if text_from_pdf:
            names = extract_names(text_from_pdf)
            dates = extract_dates(text_from_pdf)
            summary = summarize_text(text_from_pdf)

            if names:
                st.subheader("🧑 Extracted People Names:")
                for name in names:
                    st.write(name)
            else:
                st.write("No people's names found.")

            if dates:
                st.subheader("📅 Extracted Dates:")
                for date in dates:
                    st.write(date)
            else:
                st.write("No dates found.")

            if summary:
                st.subheader("📝 Summary:")
                st.write(summary)

            # PDF download
            pdf_bytes = generate_pdf_report(text_from_pdf, names, dates, summary)
            st.download_button(
                label="📄 Download Report as PDF",
                data=pdf_bytes,
                file_name="pdf_text_analysis_report.pdf",
                mime="application/pdf"
            )
        else:
            st.write("No text could be extracted from the PDF.")
