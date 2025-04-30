import streamlit as st
import spacy_streamlit
import spacy

st.title("Explore spaCy NER")

nlp = spacy.load("en_core_web_sm")
text = st.text_area("Enter text here", "Barack Obama was born on August 4, 1961.")

if text:
    doc = nlp(text)
    spacy_streamlit.visualize_ner(doc, labels=nlp.get_pipe("ner").labels)
