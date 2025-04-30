import nltk
from nltk.tokenize import word_tokenize
from nltk import pos_tag, ne_chunk

# Sample text
text = "Barack Obama was born in Honolulu, Hawaii. He was the 44th President of the United States."

# Tokenization
words = word_tokenize(text)

# POS Tagging
tagged_words = pos_tag(words)

# Named Entity Recognition (NER)
named_entities = ne_chunk(tagged_words)

# Print Named Entities
print(named_entities)
