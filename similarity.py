import streamlit as st
import pandas as pd
import numpy as np
import os
import re
import nltk
#import spacy
from nltk.data import find
from nltk.corpus import stopwords, wordnet
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict
import plotly.express as px



# Set up NLTK data path once
nltk_data_path = os.path.join(os.getcwd(), 'nltk_data')
os.makedirs(nltk_data_path, exist_ok=True)
os.environ['NLTK_DATA'] = nltk_data_path
nltk.data.path.append(nltk_data_path)

# Download required NLTK resources if not already downloaded
nltk.download('stopwords', download_dir=nltk_data_path)
nltk.download('punkt', download_dir=nltk_data_path)
nltk.download('wordnet', download_dir=nltk_data_path)
nltk.download('averaged_perceptron_tagger', download_dir=nltk_data_path)

# Initialize stopwords and lemmatizer outside the function
stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

# Helper function to convert POS tags to WordNet POS
def get_wordnet_pos(word):
    """Map POS tag to first character lemmatize() accepts"""
    tag = pos_tag([word])[0][1][0].upper()
    tag_dict = {"J": wordnet.ADJ,
                "N": wordnet.NOUN,
                "V": wordnet.VERB,
                "R": wordnet.ADV}
    return tag_dict.get(tag, wordnet.NOUN)

# Clean text function
def clean_text(text):
    # Convert to lowercase
    text = text.lower()

    # Remove HTML tags
    text = re.sub(r'<.*?>', '', text)

    # Remove non-alphabetic characters, except spaces
    text = re.sub(r'[^a-z\s]', '', text)

    # Tokenization (split the text into words)
    tokens = word_tokenize(text)

    # Remove stopwords and words with length <= 1
    tokens = [word for word in tokens if word not in stop_words and len(word) > 1]

    # Lemmatization using NLTK's WordNetLemmatizer with POS tagging
    lemmatized_tokens = [lemmatizer.lemmatize(word, get_wordnet_pos(word)) for word in tokens]

    # Rejoin tokens into a single string
    cleaned_text = " ".join(lemmatized_tokens)
    
    return cleaned_text

# Function for consine_similarity check
@st.cache_data
def check_similarity(df):
    df['Processed_Content'] = df['Content'].apply(clean_text)
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(df['Processed_Content'])
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



def create_similarity_df(source:str, pairs:defaultdict, df:pd) ->pd:
    data = []
    for i, j, similarity in pairs:
        data.append({
            "Similarity Score (%)": f"{similarity * 100:.2f}%",
            "Article 1 Title": df['Title'].iloc[i],
            "Article 2 Title": df['Title'].iloc[j],
            "Article 1 URL": df['URL'].iloc[i],
            "Article 2 URL": df['URL'].iloc[j],
        })
    return pd.DataFrame(data)






def pie_chart(pie_source, source):
    fig = px.pie(
        names = list(pie_source.keys()), 
        values=list(pie_source.values()), 
        title=f"{source}",
        hole=0.4,
    )
    st.plotly_chart(fig)
