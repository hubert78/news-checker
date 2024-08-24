import streamlit as st

st.title('Check News Plagiarism')

@st.experimental_dialog('Ghanaweb')
def ghanaweb_form():
  gw_start_date = st.date_input('Start date')
  gw_end_date = st.date_input('End date')


@st.experimental_dialog('Ghanaweb')
def joynews_form():
  gw_start_date = st.date_input('Start date')
  gw_end_date = st.date_input('End date')

col1, col2 = st.columns(2)
with col1:
  if st.button('Ghanaweb'):
    ghanaweb_form()
    
with col2:
  joynews_form()
