import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
#from collections import defaultdict
import time

from scraper import ghanaweb_multi_scraper, joynews_multi_scraper, modernghana_multi_scraper, check_duplicates
from streamlit_helper import pop_up, get_selected_data
from similarity import clean_text, cosine_check, check_similarity_scores



st.write("")
st.markdown("""
    <style>
    .centered-title {
            display: flex; justify-content: center; align-items: center; text-align: center; margin: 0; font-size: 3em; font-weight: bold;
            }
    /* Responsive design for smaller screens */
    @media (max-width: 600px) {.centered-title {font-size: 2.0em;}}
    </style>

    <div class="centered-title">Check News Similarities</div>
""", unsafe_allow_html=True)



st.write("")
st.write("")
st.write("")
source_options_1 = ['Choose news source 1', 'Ghanaweb', 'MyJoyOnline', 'Modern Ghana']
source_options_2 = ['Choose news source 2', 'Ghanaweb', 'MyJoyOnline', 'Modern Ghana']

col1, col2 = st.columns(2)
with col1:
    source_1 = st.selectbox('', source_options_1, key='source_1')
    source_1_data = pop_up(source_1)
    
with col2:
    source_2 = st.selectbox(' ', [i for i in source_options_2 if i != source_1], key='source_2')
    source_2_data = pop_up(source_2)    


# Placeholder to start scraping 
start_scraping = False

col1, col2, col3 = st.columns(3)
with col2:
    st.write("")
    st.write("")
    check_button = st.button('Search for similar articles')
    if check_button:
        st.write(f'Source 1 = {source_1}, and Source 2 = {source_2}')

        if source_1 != 'Choose news source 1' and source_2 != 'Choose news source 2':

            if not source_1_data['categories'] or not source_2_data['categories']:
                st.warning('Select news categories')

            elif source_1_data['start_date'] < source_1_data['end_date'] or source_2_data['start_date'] < source_2_data['end_date']:
                st.warning('Start date cannot be older than End date')       

            elif source_1_data['start_date'] > datetime.now().date() or source_2_data['start_date'] > datetime.now().date():
                st.warning('Start Date cannot be in the future')
            else:
                start_scraping = True


source_1_df = pd.DataFrame(columns=["Source", "Category", "Date Posted", "Title", "URL", "Content"])
source_2_df = pd.DataFrame(columns=["Source", "Category", "Date Posted", "Title", "URL", "Content"])
comibned_df = pd.DataFrame(columns=["Source", "Category", "Date Posted", "Title", "URL", "Content"])

if start_scraping:
    # Scrap the first news source
    if source_1 == 'Ghanaweb':
        source_1_df = ghanaweb_multi_scraper(source_1_data)

    elif source_1 == 'MyJoyOnline':
        source_1_df = joynews_multi_scraper(source_1_data)

    elif source_1 == 'Modern Ghana':
        source_1_df = modernghana_multi_scraper(source_1_data)

    # Check for any duplicates
    if source_1_df is not None and not source_1_df.empty:
        source_1_df_cleaned = check_duplicates(source_1_df)
        st.write(source_1_df_cleaned.head())


    # Scrap the second news source
    if source_2 == 'Ghanaweb':
        source_2_df = ghanaweb_multi_scraper(source_2_data)

    elif source_2 == 'MyJoyOnline':
        source_2_df = joynews_multi_scraper(source_2_data)

    elif source_2 == 'Modern Ghana':
        source_2_df = modernghana_multi_scraper(source_2_data)

    # Check for any duplicates
    if source_2_df is not None and not source_2_df.empty:
        source_2_df_cleaned = check_duplicates(source_2_df)
        st.write(source_2_df_cleaned.head())

    # Combine the two scraped dataframes
    if source_1_df is not None and not source_1_df.empty and source_2_df is not None and not source_2_df.empty:
        comibned_df = pd.concat([source_1_df_cleaned, source_2_df_cleaned], axis=0, ignore_index=True)

    

        # Preprocess and check for similarity scores.
        #data_scores = {}

        st.write(comibned_df.head())
        with st.spinner(f'Checking Similarity'):
            comibned_df['Processed_Content'] = comibned_df['Content'].apply(clean_text)
            similarity_matrix = cosine_check(comibned_df['Processed_Content'])

            # Threshold for plagiarism
            threshold = 0.7
            data_scores = check_similarity_scores(threshold, similarity_matrix, comibned_df)


    #if data_scores:
        between_source_pairs = data_scores['between_source_pairs']

        num_of_articles = len(between_source_pairs[source_1, source_2])
        st.header(f"There are {num_of_articles} plagiarized articles between {source_1} and {source_2}")





















