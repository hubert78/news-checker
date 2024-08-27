import streamlit as st
from datetime import datetime, timedelta


# Ghanaweb form
def ghanaweb_form():
    categories = ["NewsArchive", "business", "entertainment", "africa", "SportsArchive", "features"]
    gw_start_date = st.date_input('Start date', key='gw_start_date')
    gw_end_date = st.date_input('End date', key='gw_end_date')
    gw_categories = st.multiselect('Select news categories', categories, key='gw_categories')
 
    ghanaweb_data = {'start_date': gw_start_date,
                    'end_date': gw_end_date,
                    'categories': gw_categories,}
    return ghanaweb_data

def new3_form():
    categories = ["news", "elections", "business", "showbiz", "sports", "health", "opinion"]
    new3_start_date = st.date_input('Start date', key='new3_start_date')
    new3_end_date = st.date_input('End date', key='new3_end_date')
    new3_categories = st.multiselect('Select news categories', categories, key='new3_categories')
 
    new3_data = {'start_date': new3_start_date,
                    'end_date': new3_end_date,
                    'categories': new3_categories,}
    return new3_data


# Joy News form
def joynews_form():
    categories = ['news', 'business', 'entertainment', 'sports', 'opinion']
    jn_start_date = st.date_input('Start date', key='jn_start_date')
    jn_end_date = st.date_input('End date', key='jn_end_date')
    jn_categories = st.multiselect('Select news categories', categories, key='jn_categories')
    joynews_data = {'start_date': jn_start_date,
                    'end_date': jn_end_date,
                    'categories': jn_categories,}
    return joynews_data



# Modern Ghana form
def modernghana_form():
    mdg_start_date = st.date_input('Start date', key='mdg_start_date')
    mdg_end_date = st.date_input('End date', key='mdg_end_date')
    st.write('No article categories available now')
    mdg_categories = [" "]
    modernghana_data = {'start_date': mdg_start_date,
                        'end_date': mdg_end_date,
                        'categories': mdg_categories,}
    return modernghana_data


# Yen Ghana form
def yenghana_form():
    categories = ['Ghana', 'Politics', 'Business', 'Entertanment', 'Sports', 'World']
    yen_start_date = st.date_input('Start date', key='yen_start_date')
    yen_end_date = st.date_input('End date', key='yen_end_date')
    yen_categories = st.multiselect('Select news categories', categories, key='yen_categories')
    yenghana_data = {'start_date': yen_start_date,
                     'end_date': yen_end_date,
                     'categories': yen_categories,}
    return yenghana_data


def pop_up(source):
    #try:
    if source == 'Ghanaweb':
        return ghanaweb_form()
    elif source == '3News':
        return new3_form()
    elif source == 'MyJoyOnline':
        return joynews_form()
    elif source == 'Modern Ghana':
        return modernghana_form()
    elif source == 'Yen Ghana':
        return yenghana_form()



def get_selected_data(state):
    start = st.session_state[state]['start_date']
    end = st.session_state[state]['end_date']

    start_date = st.session_state[state]['start_date'].strftime('%Y%m%d')
    end_date = st.session_state[state]['end_date'].strftime('%Y%m%d')

    categories = st.session_state[state]['categories']
    return {
        'start': start, 'end': end, 'start_date': start_date, 'end_date': end_date, 'categories': categories,
    }





