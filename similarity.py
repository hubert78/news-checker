import pandas as pd
import numpy as np
import os
import re
import nltk
import spacy
from nltk.data import find
from nltk.corpus import stopwords, wordnet
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
#from collections import defaultdict





# Set the path to your uploaded spaCy model
model_path = 'en_core_web_sm'
nlp = spacy.load(model_path)
#nlp = spacy.load('/path/to/en_core_web_sm-3.7.1')

def clean_text(text):

    # Convert to lowercase
    text = text.lower()

    # Remove HTML tags
    text = re.sub(r'<.*?>', '', text)

    # Remove non-alphabetic characters, except spaces
    text = re.sub(r'[^a-z\s]', '', text)

    # Process the text with spaCy
    doc = nlp(text)

    # Lemmatize, remove stopwords, and non-alphabetic tokens
    tokens = [
        token.lemma_ for token in doc
        if not token.is_stop and token.is_alpha
    ]

    # Rejoin tokens into a single string
    cleaned_text = " ".join(tokens)
    
    return cleaned_text



# Function for consine_similarity check
def cosine_check(df):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(df)
    similarity_matrix = cosine_similarity(tfidf_matrix)
    return similarity_matrix



# Function to process the similiarity matrix obtained.
def check_similarity_scores(threshold, similarity_matrix, df):
    
    data_scores = {}
 
    plagiarism_pairs = np.argwhere(similarity_matrix > threshold)

    plagiarism_pairs = [(i, j) for i, j in plagiarism_pairs if i != j]

    # A dictionary counters for within-source and between-source similarities
    within_source_pairs = defaultdict(list)
    between_source_pairs = defaultdict(list)

    # A dictionary counter to count plagiarism occurrences per category and date
    category_pairs  = defaultdict(int)
    source1_categories = defaultdict(int)
    source2_categories = defaultdict(int)
    source1_date_count = defaultdict(int)
    source2_date_count = defaultdict(int)

    # To ensure each pair is counted only once, use a set to track counted pairs
    seen_pairs = set()

    # Display potential plagiarism cases
    for i, j in plagiarism_pairs:
        # Make sure (i, j) is not counted more than once
        if (i, j) not in seen_pairs and (j, i) not in seen_pairs:
            seen_pairs.add((i, j))  # Mark the pair as counted

            if df['Source'].iloc[i] == df['Source'].iloc[j]:
                # Group within-source similarities
                within_source_pairs[df['Source'].iloc[i]].append((i, j, similarity_matrix[i, j]))
            else:
                # Group between-source similarities
                between_source_pairs[(df['Source'].iloc[i], df['Source'].iloc[j])].append((i, j, similarity_matrix[i, j]))

                # Count the number of articles plagiarized in each category
                category_i = df['Category'].iloc[i]
                category_j = df['Category'].iloc[j]

                source1_categories[category_i] +=1
                source2_categories[category_j] +=1


                # Increase the plagiarism count for the category
                category_pairs[(category_i, category_j)] += 1

                # Count the number of articles plagiarized per each date
                date_i = df['Date Posted'].iloc[i]
                date_j = df['Date Posted'].iloc[j]

                # Increase the plagiarism count for each date
                source1_date_count[date_i] += 1
                source2_date_count[date_j] += 1
                
    data_scores = {
        'within_source_pairs': within_source_pairs,
        'between_source_pairs': between_source_pairs,
        'category_pairs': category_pairs,
        'source1_categories': source1_categories,
        'source2_categories': source2_categories,
        'source1_date_count': source1_date_count, 
        'source2_date_count': source2_date_count,
    }
    return data_scores
