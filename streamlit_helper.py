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


# Joy News form
#@st.dialog('Joy News')
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
#@st.dialog('Modern Ghana')
def modernghana_form():
    mdg_start_date = st.date_input('Start date', key='mdg_start_date')
    mdg_end_date = st.date_input('End date', key='mdg_end_date')
    st.write('No article categories available now')
    mdg_categories = [" "]
    modernghana_data = {'start_date': mdg_start_date,
                        'end_date': mdg_end_date,
                        'categories': mdg_categories,}
    return modernghana_data


def pop_up(source):
    #try:
    if source == 'Ghanaweb':
        return ghanaweb_form()
    elif source == 'MyJoyOnline':
        return joynews_form()
    elif source == 'Modern Ghana':
        return modernghana_form()
    #except:
        #st.info('Only one news source enabled. Refresh page')



def get_selected_data(state):
    start = st.session_state[state]['start_date']
    end = st.session_state[state]['end_date']

    start_date = st.session_state[state]['start_date'].strftime('%Y%m%d')
    end_date = st.session_state[state]['end_date'].strftime('%Y%m%d')

    categories = st.session_state[state]['categories']
    return {
        'start': start, 'end': end, 'start_date': start_date, 'end_date': end_date, 'categories': categories,
    }





