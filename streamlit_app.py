import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scraper import ghanaweb_scraper, joynews_scraper, clean_text
import re
import nltk

import spacy.cli
spacy.cli.download("en_core_web_sm")
import spacy

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from collections import defaultdict

import subprocess
subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])


st.title('Check News Plagiarism')

# Ghanaweb form
@st.dialog('Ghanaweb')
def ghanaweb_form():
    categories = ["NewsArchive", "business", "entertainment", "africa", "SportsArchive", "features"]
    gw_start_date = st.date_input('Start date')
    gw_end_date = st.date_input('End date')
    gw_categories = st.multiselect('Select news categories', categories)
    
    gw_num = st.text_input('Enter number')
    gw_submit = st.button('Submit')
    if gw_submit:
        st.session_state['gw_response'] = {'start_date': gw_start_date,
                                           'end_date': gw_end_date,
                                           'categories': gw_categories,
                                           'gw_num': gw_num,
                                          }
        st.rerun()

# Joy News form
@st.dialog('Joy News')
def joynews_form():
    categories = ['news', 'business', 'entertainment', 'sports', 'opinion']

    jn_start_date = st.date_input('Start date')
    jn_end_date = st.date_input('End date')
    jn_categories = st.multiselect('Select Categories', categories)

    
    jn_num = st.text_input('Enter number')
    jn_submit = st.button('Submit')
    if jn_submit:
        st.session_state['jn_response'] = {'start_date': jn_start_date,
                                           'end_date': jn_end_date,
                                           'categories': jn_categories,
                                           'jn_num': jn_num,
                                          }
        st.rerun()


col1, col2 = st.columns(2)
with col1:
  gw_button = st.button('Ghanaweb')
  if gw_button:
    gw_num = ghanaweb_form()
    
with col2:
  jn_button = st.button('Joy News')
  if jn_button:
    jn_num = joynews_form()

check_button = st.button('Check for plagiarism')


# Placeholder to start scraping 
start_scraping = False

# Display results 
if 'gw_response' in st.session_state and 'jn_response' in st.session_state and check_button:

    gw_start = st.session_state['gw_response']['start_date']
    gw_end = st.session_state['gw_response']['end_date']
    jn_start = st.session_state['jn_response']['start_date']
    jn_end = st.session_state['jn_response']['end_date']
    
    gw_start_date = st.session_state['gw_response']['start_date'].strftime('%Y%m%d')
    gw_end_date = st.session_state['gw_response']['end_date'].strftime('%Y%m%d')
    jn_start_date = st.session_state['jn_response']['start_date']
    jn_end_date = st.session_state['jn_response']['end_date'].strftime('%Y-%m-%d')
    gw_categories = st.session_state['gw_response']['categories']
    jn_categories = st.session_state['jn_response']['categories']
    
    # Check if input Date is valid for scraping.
    if gw_start < gw_end or jn_start < jn_end:
        st.info('Select an End Date older or equal to Start Date')
        
    elif gw_start > datetime.now().date() or jn_start > datetime.now().date():
        st.info('Start Date cannot be in the future')
    else:
        start_scraping = True



df_ghanaweb = pd.DataFrame(columns=["Source", "Category", "Date Posted", "Title", "URL", "Content"])
df_joynews = pd.DataFrame(columns=["Source", "Category", "Date Posted", "Title", "URL", "Content"])
articles = pd.DataFrame(columns=["Source", "Category", "Date Posted", "Title", "URL", "Content"])

if start_scraping == True:
    # Scraping news from Ghanaweb
    for category in gw_categories:
        with st.spinner(f'Scraping news from Ghanaweb. Category = {category}'):
            df = ghanaweb_scraper(category, gw_end_date, gw_start_date)
            if df is not None and not df.empty:
                df_ghanaweb = pd.concat([df_ghanaweb, df], axis=0, ignore_index=True)

    # Remove duplicated rows with the same URL
    if df_ghanaweb is not None and not df_ghanaweb.empty:
        df_ghanaweb = df_ghanaweb.drop_duplicates(subset=['URL'])
        st.info('Ghanaweb scraping complete.')
    else:
        st.info('Failed to scrap news from ghanaweb.com')


    # Scraping news from Joynews
    categories = {
        "news": ["national", "politics", "crime", "africa" "regional", "technology", "oddly-enough", "diaspora", "international", "health", "education", "obituary"],
        "business": ["economy", "energy", "finance", "investments", "mining", "agribusiness", "real-estate", "stocks", "telecom", "aviation", "banking", "technology-business"],
        "entertainment": ["movies", "music", "radio-tv", "stage", "art-design", "books"],
        "sports": ["football", "boxing", "athletics", "tennis", "golf", "other-sports"],
        "opinion": [""],
    }
    
    for category in categories:
        if category in jn_categories:
            with st.spinner(f'Scraping news from MyJoyOnline. Category = {category}'):
                for sub_category in categories[category]:
                    df = joynews_scraper(category, sub_category, jn_end_date)
                    if df is not None and not df.empty:
                        df_joynews = pd.concat([df_joynews, df], axis=0, ignore_index=True)

    if df_joynews is not None and not df_joynews.empty:
        df_joynews = df_joynews.drop_duplicates(subset=['URL'])
        st.info('MyJoyOnline scraping complete.')
    else:
        st.info('Failed to scrap news from myjoyonline.com')


    if df_ghanaweb is not None and not df_ghanaweb.empty and df_joynews is not None and not df_joynews.empty:
        articles = pd.concat([df_ghanaweb, df_joynews], axis=0, ignore_index=True)
    
if articles is not None and not articles.empty:
    st.write(articles.head())
    with st.spinner(f'Processing data for plagiarism comparison'):
        # Download stopwords from NLTK
        nltk.download('stopwords')
        nltk.download('punkt')
        
        # Load Spacy's English model for lemmatization
        nlp = spacy.load('en_core_web_sm')
        
        # Set of English stopwords
        stop_words = set(stopwords.words('english'))
    
        articles['Processed_Content'] = articles['Content'].apply(clean_text)


    with st.spinner(f'Checking Similarity'):
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(articles['Processed_Content'])
        similarity_matrix = cosine_similarity(tfidf_matrix)

        # Define a threshold for plagiarism
        threshold = 0.7
        
        # Find article pairs with cosine similarity above the threshold
        plagiarism_pairs = np.argwhere(similarity_matrix > threshold)
        
        # Filter out self-pairs (article compared with itself)
        plagiarism_pairs = [(i, j) for i, j in plagiarism_pairs if i != j]
        
        # A dictionary counters for within-source and between-source similarities
        within_source_pairs = defaultdict(list)
        between_source_pairs = defaultdict(list)
        
        # A dictionary counter to count plagiarism occurrences per category and date
        category_pairs  = defaultdict(int)
        source1_date_count = defaultdict(int)
        source2_date_count = defaultdict(int)
        
        # To ensure each pair is counted only once, use a set to track counted pairs
        seen_pairs = set()
        
        # Display potential plagiarism cases
        for i, j in plagiarism_pairs:
            # Make sure (i, j) is not counted more than once
            if (i, j) not in seen_pairs and (j, i) not in seen_pairs:
                seen_pairs.add((i, j))  # Mark the pair as counted
                
                # Check if the articles are from the same source
                if articles['Source'].iloc[i] == articles['Source'].iloc[j]:
                    # Group within-source similarities
                    within_source_pairs[articles['Source'].iloc[i]].append((i, j, similarity_matrix[i, j]))
                else:
                    # Group between-source similarities
                    between_source_pairs[(articles['Source'].iloc[i], articles['Source'].iloc[j])].append((i, j, similarity_matrix[i, j]))
                    
                    # Count the number of articles plagiarized in each category
                    category_i = articles['Category'].iloc[i]
                    category_j = articles['Category'].iloc[j]
        
                    # Increase the plagiarism count for the category
                    category_pairs[(category_i, category_j)] += 1
                    
                    # Count the number of articles plagiarized per each date
                    date_i = articles['Date Posted'].iloc[i]
                    date_j = articles['Date Posted'].iloc[j]
                    
                    # Increase the plagiarism count for each date
                    source1_date_count[date_i] += 1
                    source2_date_count[date_j] += 1



if articles is not None and not articles.empty:
    num_of_articles = len(between_source_pairs['GhanaWeb', 'My Joy Online'])
    st.header(f"There are {num_of_articles} plagiarized articles between Ghanaweb and My Joyonline")




















