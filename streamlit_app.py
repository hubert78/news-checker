import streamlit as st

st.title('Check News Plagiarism')

@st.experimental_dialog('Ghanaweb')
def ghanaweb_form():
  gw_start_date = st.date_input('Start date')
  gw_end_date = st.date_input('End date')
  gw_num = st.text_input('Enter number')
  return gw_num


@st.experimental_dialog('Joy News Online')
def joynews_form():
  jn_start_date = st.date_input('Start date')
  jn_end_date = st.date_input('End date')
  jn_num = st.text_input('Enter number')
  return jn_num

col1, col2 = st.columns(2)
with col1:
  if st.button('Ghanaweb'):
    gw_num = ghanaweb_form()
    
with col2:
  if st.button('Joy News'):
    jn_num = joynews_form()


st.write(int(gw_num) + int(jn_num))
