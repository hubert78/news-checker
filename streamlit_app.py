import streamlit as st
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
from collections import defaultdict
import time
import plotly.express as px

from scraper import ghanaweb_multi_scraper, joynews_multi_scraper, modernghana_multi_scraper, yenghana_multi_scraper, new3_multi_scraper, check_duplicates
from streamlit_helper import pop_up, get_selected_data
from similarity import check_similarity, check_similarity_scores, create_similarity_df, pie_chart



st.set_page_config(layout="wide")

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

start_col1, start_col2, start_col3 = st.columns([1, 5, 1])
with start_col2:

    source_options_1 = ['Choose news source 1', 'Ghanaweb', '3News', 'MyJoyOnline', 'Yen Ghana', 'Modern Ghana']
    source_options_2 = ['Choose news source 2', 'Ghanaweb', '3News', 'MyJoyOnline', 'Yen Ghana', 'Modern Ghana']

    col1, col2 = st.columns(2)
    with col1:
        source_1 = st.selectbox('', source_options_1, key='source_1')
        source_1_data = pop_up(source_1)
        
    with col2:
        source_2 = st.selectbox(' ', [i for i in source_options_2 if i != source_1], key='source_2')
        source_2_data = pop_up(source_2)    


    # Placeholder to start scraping 
    start_scraping = False

    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        threshold = st.slider('Select a similarity threshold', 35, 100, 70)

    col1, col2, col3 = st.columns([1.5, 1.5, 1.5])
    with col2:
        #st.write("")
        check_button = st.button('Get a similarity report')
        if check_button:
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

    start_analysis = False

    if start_scraping:
        # Scrap the first news source
        if source_1 == 'Ghanaweb':
            source_1_df = ghanaweb_multi_scraper(source_1_data)

        if source_1 == '3News':
            source_1_df = new3_multi_scraper(source_1_data)

        elif source_1 == 'MyJoyOnline':
            source_1_df = joynews_multi_scraper(source_1_data)

        elif source_1 == 'Modern Ghana':
            source_1_df = modernghana_multi_scraper(source_1_data)

        elif source_1 == 'Yen Ghana':
            source_1_df = yenghana_multi_scraper(source_1_data)

        # Check for any duplicates
        if source_1_df is not None and not source_1_df.empty:
            source_1_df_cleaned, source_1_duplicate = check_duplicates(source_1_df)
            #st.write(source_1_df_cleaned.head())


        # Scrap the second news source
        if source_2 == 'Ghanaweb':
            source_2_df = ghanaweb_multi_scraper(source_2_data)

        if source_2 == '3News':
            source_2_df = new3_multi_scraper(source_2_data)

        elif source_2 == 'MyJoyOnline':
            source_2_df = joynews_multi_scraper(source_2_data)

        elif source_2 == 'Modern Ghana':
            source_2_df = modernghana_multi_scraper(source_2_data)
        
        elif source_2 == 'Yen Ghana':
            source_2_df = yenghana_multi_scraper(source_2_data)

        # Check for any duplicates
        if source_2_df is not None and not source_2_df.empty:
            source_2_df_cleaned, source_2_duplicate = check_duplicates(source_2_df)
            #st.write(source_2_df_cleaned.head())

        # Combine the two scraped dataframes
        if source_1_df is not None and not source_1_df.empty and source_2_df is not None and not source_2_df.empty:
            comibned_df = pd.concat([source_1_df_cleaned, source_2_df_cleaned], axis=0, ignore_index=True)


            # Preprocess and check for similarity scores.
            with st.spinner(f'Checking Similarity'):
                #comibned_df['Processed_Content'] = comibned_df['Content'].apply(clean_text)
                similarity_matrix = check_similarity(comibned_df)

                # Threshold for plagiarism
                threshold = threshold/100
                data_scores = check_similarity_scores(threshold, similarity_matrix, comibned_df)

                between_source_pairs = data_scores['between_source_pairs']
                num_articles = len(between_source_pairs[source_1, source_2])

                st.write('')
                col1, col2, col3 = st.columns([1, 4, 1])
                with col2:
                    st.subheader(f'Plagiarism Report: {num_articles} Articles Found')
                if num_articles > 0:
                    start_analysis = True




if start_analysis:
    big_col1, big_col2 = st.columns([3, 2])
    
    with big_col1:
        st.markdown('#### Proportion of articles plagiarized by source')

        between_source_pairs = data_scores['between_source_pairs']
        num_articles = len(between_source_pairs[source_1, source_2])

        pie_source_1 = {
            'Plagiarized articles': num_articles, 
            'Unplagiarized articles': source_1_df_cleaned.shape[0]-num_articles
            }
        pie_source_2 = {
            'Plagiarized articles': num_articles, 
            'Unplagiarized articles': source_2_df_cleaned.shape[0]-num_articles
            }

        col1, col2 = st.columns(2)
        with col1:
            pie_chart(pie_source_1, source_1)

        with col2:
            pie_chart(pie_source_2, source_2)
        
    with big_col2:

        st.markdown('#### Most plagiarized news category')
        source_1_categories, source_2_categories = data_scores['source1_categories'], data_scores['source2_categories']
        source_1_categories = {k: v for k, v in source_1_categories.items() if k != 'category' and v != 0} 
        source_1_categories = dict(sorted(source_1_categories.items(), key=lambda item: item[1], reverse=True))

        source_2_categories = {k: v for k, v in source_2_categories.items() if k != 'category' and v != 0} 
        source_2_categories = dict(sorted(source_2_categories.items(), key=lambda item: item[1], reverse=True))

        col1, col2 = st.columns(2)
        with col1:
            fig = px.bar(
                x = list(source_1_categories.keys()), 
                y = list(source_1_categories.values()), 
                title = source_1,
                labels = {'x': 'Category', 'y': 'Number of Articles'},
            )
            st.plotly_chart(fig)
        with col2:
            fig = px.bar(
                x = list(source_2_categories.keys()), 
                y = list(source_2_categories.values()), 
                title = source_2,
                labels = {'x': 'Category', 'y': 'Number of Articles'},
            )
            st.plotly_chart(fig)


if start_analysis:
    #with st.expander("Some news websites also had multiple articles that were similar"):
    big_col1, big_col2 = st.columns(2)

    with big_col1:
        st.markdown('#### Different URL but similar content')

        within_source_pairs = data_scores['within_source_pairs']

        num_articles_similar_1 = len(within_source_pairs[source_1])
        num_articles_similar_2 = len(within_source_pairs[source_2])

        pie_source_1 = {
            'Similar articles': num_articles_similar_1, 
            'Different articles': source_1_df_cleaned.shape[0]-num_articles_similar_1
            }
        pie_source_2 = {
            'Similar articles': num_articles_similar_2, 
            'Different articles': source_2_df_cleaned.shape[0]-num_articles_similar_2
            }

        col1, col2 = st.columns(2)
        with col1:
            pie_chart(pie_source_1, source_1)

        with col2:
            pie_chart(pie_source_2, source_2)

    with big_col2:
        st.markdown('#### Articles with duplicated URL')
        col1, col2 = st.columns(2)
        if source_1_duplicate > 0:
            pie_source_1 = {
                'Duplicated URL': source_1_duplicate, 
                'Different URL': source_1_df.shape[0]-source_1_duplicate
                }
            with col1:
                pie_chart(pie_source_1, source_1)


        if source_2_duplicate > 0:
            pie_source_2 = {
                'Duplicated URL': source_2_duplicate, 
                'Different URL': source_2_df.shape[0]-source_2_duplicate
                }
            with col2:
                pie_chart(pie_source_2, source_2)



if start_analysis:
    #with st.expander("Some news websites also had multiple articles that were similar"):
    st.markdown('#### Date with most plagiarized articles')
    big_col1, big_col2 = st.columns(2)

    with big_col1:
        source_1_date_count = data_scores['source1_date_count']

        fig = px.bar(
            y = list(source_1_date_count.keys()), 
            x = list(source_1_date_count.values()), 
            title = source_1,
            labels = {'y': 'Date', 'x': 'Number of Articles'},
            orientation = 'h',
        )
        st.plotly_chart(fig)

    with big_col2:
        source_2_date_count = data_scores['source2_date_count']

        fig = px.bar(
            y = list(source_2_date_count.keys()), 
            x = list(source_2_date_count.values()), 
            title = source_2,
            labels = {'y': 'Date', 'x': 'Number of Articles'},
            orientation = 'h',
        )
        st.plotly_chart(fig) 


if start_analysis:
    between_source_pairs = data_scores['between_source_pairs']
    plagiarized_data = []

    # Iterate through the pairs and collect details
    for (source1, source2), pairs in between_source_pairs.items():
        for i, j, similarity in pairs:
            plagiarized_data.append({
                'Similarity score': f"{similarity*100:.2f}%",
                f'{source_1} Article Title': comibned_df['Title'].iloc[i],
                f'{source_2} Article Title': comibned_df['Title'].iloc[j],
                f'{source_1} Article URL': comibned_df['URL'].iloc[i],
                f'{source_2} Article URL': comibned_df['URL'].iloc[j]
            })
        # Create DataFrame from the collected data
    plagiarized_data = pd.DataFrame(plagiarized_data)

    with st.expander(f"Articles plagiarized between {source_1} and {source_2}"):
        st.markdown(f'##### {plagiarized_data.shape[0]} articles detected')
        st.dataframe(plagiarized_data)

    source_1_similarity_within = create_similarity_df(source_1, within_source_pairs[source_1], comibned_df)
    source_2_similarity_within = create_similarity_df(source_2, within_source_pairs[source_2], comibned_df)

    with st.expander(f"Articles with similar content from {source_1}"):
        st.markdown(f'##### {source_1_similarity_within.shape[0]} articles detected')
        st.dataframe(source_1_similarity_within)

    with st.expander(f" Articles with similar content from {source_2}"):
        st.markdown(f'##### {source_2_similarity_within.shape[0]} articles detected')
        st.dataframe(source_2_similarity_within)




