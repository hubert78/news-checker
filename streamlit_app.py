import streamlit as st

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
                                           'gw_categories': gw_categories,
                                           'gw_num': gw_num,
                                          }
        st.rerun()

# Joy News form
@st.dialog('Joy News')
def joynews_form():
    categories = ['news', 'business', 'entertainment', 'sports', 'opinion']

    jn_start_date = st.date_input('Start date')
    jn_end_date = st.date_input('End date')
    jn_categories = st.multiselect('Select Categories', cateogories)

    
    jn_num = st.text_input('Enter number')
    jn_submit = st.button('Submit')
    if jn_submit:
        st.session_state['jn_response'] = {'start_date': jn_start_date,
                                           'end_date': jn_end_date,
                                           'jn_categories': jn_categories,
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
    

# Display results
if 'gw_response' in st.session_state and 'jn_response' in st.session_state and check_button:
    gw_num = st.session_state['gw_response']['gw_num']
    jn_num = st.session_state['jn_response']['jn_num']
    st.write(int(gw_num) + int(jn_num))
