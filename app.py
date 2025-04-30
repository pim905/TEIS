import streamlit as st
import spacy

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

# App title
st.title("Simple spaCy NER Test")

# Text input
text = st.text_area("Enter some text:", "Barack Obama was born on August 4, 1961.")

# Process and display entities
if text:
    doc = nlp(text)
    st.subheader("Named Entities")
    for ent in doc.ents:
        st.write(f"{ent.text} ({ent.label_})")
