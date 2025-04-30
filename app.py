import streamlit as st
import spacy

st.title("spaCy Entity Recognizer")

try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    st.error("Model not found. Try restarting or reinstalling.")
    st.stop()

text = st.text_area("Enter some text", "Elon Musk was born on June 28, 1971.")

if text:
    doc = nlp(text)
    st.subheader("Named Entities")
    for ent in doc.ents:
        st.write(f"{ent.text} ({ent.label_})")
