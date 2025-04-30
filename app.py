import streamlit as st
from openai import OpenAI
import PyPDF2
from docx import Document

# Initialize OpenAI client with your API key
client = OpenAI(api_key="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")

st.set_page_config(page_title="Name and Date Extractor", layout="centered")
st.title("📄 AI Name & Date Extractor")

st.markdown("Upload a document (`.pdf`, `.docx`, or `.txt`), and this app will extract **people's names** and **dates** using OpenAI.")

uploaded_file = st.file_uploader("Choose a file", type=["pdf", "docx", "txt"])

def read_file(file):
    if file.name.endswith(".pdf"):
        try:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text
        except Exception as e:
            st.error(f"Error reading PDF: {e}")
            return ""
    elif file.name.endswith(".docx"):
        try:
            doc = Document(file)
            return "\n".join([para.text for para in doc.paragraphs])
        except Exception as e:
            st.error(f"Error reading DOCX: {e}")
            return ""
    elif file.name.endswith(".txt"):
        try:
            return file.read().decode("utf-8")
        except Exception as e:
            st.error(f"Error reading TXT: {e}")
            return ""
    else:
        st.warning("Unsupported file format.")
        return ""

def extract_names_dates(text):
    prompt = (
        "Extract all names of people and all dates from the following text. "
        "Return the results in two separate lists: one for names, one for dates. "
        "List names only once each. Use plain formatting.\n\n"
        f"Text:\n{text}"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Use GPT-3.5 instead of GPT-4
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"OpenAI API error: {e}")
        return ""

if uploaded_file:
    st.subheader("📃 Extracting Text")
    text = read_file(uploaded_file)
    
    if text:
        with st.expander("View raw text from file"):
            st.text_area("File Text", text, height=200)
        
        st.subheader("🔍 Extracted Names & Dates")
        with st.spinner("Analyzing with OpenAI..."):
            result = extract_names_dates(text)
        st.success("Extraction complete!")
        st.text(result)
    else:
        st.warning("No text extracted from file.")
