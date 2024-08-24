import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scraper import ghanaweb_scraper, joynews_scraper


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

    gw_start_date = st.session_state['gw_response']['start_date']
    gw_end_date = st.session_state['gw_response']['end_date']
    jn_start_date = st.session_state['jn_response']['start_date']
    jn_end_date = st.session_state['jn_response']['end_date']
    gw_categories = st.session_state['gw_response']['categories']
    jn_categories = st.session_state['jn_response']['categories']
    
    # Check if input Date is valid for scrapping.
    if gw_start_date < gw_end_date or jn_start_date < jn_end_date:
        st.info('Select an End Date older or equal to Start Date')
    elif gw_start_date > datetime.now().date() or jn_start_date > datetime.now().date():
        st.info('Start Date cannot be in the future')
    else:
        st.write(gw_start_date)
        start_scraping = True



df_ghanaweb = pd.DataFrame(columns=["Source", "Category", "Date Posted", "Title", "URL", "Content"])
df_joynews = pd.DataFrame(columns=["Source", "Category", "Date Posted", "Title", "URL", "Content"])
articles = pd.DataFrame(columns=["Source", "Category", "Date Posted", "Title", "URL", "Content"])

if start_scraping == True:
    # Scraping news from Ghanaweb
    for category in gw_categories:
        with st.spinner(f'Scraping news from Ghanaweb. Category = {category}'):
            df = ghanaweb_scrapper(category, gw_end_date, gw_start_date)
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
    
if df_ghanaweb is not None and not df_ghanaweb.empty:
    st.write(article.head())

    gw_num = st.session_state['gw_response']['gw_num']
    jn_num = st.session_state['jn_response']['jn_num']
    st.write(int(gw_num) + int(jn_num))

























