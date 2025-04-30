import streamlit as st
import nltk
from nltk.tokenize import word_tokenize
from nltk import pos_tag, ne_chunk

# Download necessary NLTK resources
nltk.download('punkt')
nltk.download('maxent_ne_chunker')
nltk.download('words')
nltk.download('averaged_perceptron_tagger')  # Add this line

# Function to extract names from text
def extract_names(text):
    # Tokenize the input text
    words = word_tokenize(text)
    
    # POS tagging
    tagged_words = pos_tag(words)
    
    # Named Entity Recognition (NER)
    named_entities = ne_chunk(tagged_words)
    
    # Extract PERSON entities
    people_names = []
    for chunk in named_entities:
        if isinstance(chunk, nltk.Tree):
            if chunk.label() == 'PERSON':
                # Join the words that make up the person's name
                name = " ".join([word for word, tag in chunk])
                people_names.append(name)
    
    return people_names

# Streamlit app interface
st.title("Named Entity Recognition (NER) with NLTK")

# Input area for user to paste text
text_input = st.text_area("Paste your text here:")

# Button to extract names
if st.button('Extract Names'):
    if text_input:
        names = extract_names(text_input)
        if names:
            st.subheader("Extracted People Names:")
            for name in names:
                st.write(name)
        else:
            st.write("No people's names found in the text.")
    else:
        st.write("Please paste some text to extract names.")
