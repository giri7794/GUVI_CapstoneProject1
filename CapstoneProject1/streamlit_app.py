import streamlit as st
from youtube_api import YouTubeClient

# YouTube API key
api_key = 'AIzaSyDRmdQPNoRGO2u0XdO38m5Le5Mhsj-441E'

# Initialize YouTubeClient
youtube_client = YouTubeClient(api_key)

# Streamlit app
st.title('YouTube Channel Information')

channel_id = st.text_input('Enter YouTube Channel ID:')
if st.button('Get Channel Details'):
    if channel_id:
        details = youtube_client.get_channel_details(channel_id)
        st.write(details)
    else:
        st.error('Please enter a YouTube channel ID.')