import streamlit as st
import pandas as pd
import json

from googleapiclient.errors import HttpError
from youtube_api import YouTubeClient
from mangodb_handler import MongoDBHandler


def json_to_dict(data):
    if isinstance(data, str):
        return json.loads(data)
    return data


class ChannelIDManagerApp:
    def __init__(self):
        self.youtube_client = YouTubeClient('AIzaSyDRmdQPNoRGO2u0XdO38m5Le5Mhsj-441E')
        self.mongo_handler = MongoDBHandler("mongodb://localhost:27017", "YTDataLake")
        # Initialize session state for storing channel IDs
        if 'channels' not in st.session_state:
            st.session_state.channels = pd.DataFrame(columns=['Channel ID'])
        if 'new_channel_id' not in st.session_state:
            st.session_state.new_channel_id = ""

    @staticmethod
    def add_channel_id(channel_id):
        if channel_id:
            st.session_state.channels = pd.concat([
                st.session_state.channels,
                pd.DataFrame([[channel_id]], columns=['Channel ID'])
            ], ignore_index=True)
            # Clear input after adding
            st.session_state.new_channel_id = ""

    @staticmethod
    def delete_channel_id(self, index):
        st.session_state.channels = st.session_state.channels.drop(index).reset_index(drop=True)

    def fetch_data_from_source(self, channel_id: str):
        # Initialize empty data variables
        playlist_data = []
        video_data = []
        comment_data = []

        try:
            # Fetch and insert channel details
            channel_data = self.youtube_client.get_channel_details(channel_id)
            self.mongo_handler.insert_channel(channel_data)
            # st.write(f"channel_data : {type(channel_data)}")
        except Exception as e:
            st.write(f"Error fetching or inserting channel {channel_id}: {e}")

        try:
            # Fetch playlists
            playlist_data = self.youtube_client.get_playlists(channel_id)
            for playlist_info in playlist_data:
                self.mongo_handler.insert_playlist(json_to_dict(playlist_info))
                # st.write(f"playlist_info : {type(json_to_dict(playlist_info))}")

                try:
                    # Fetch videos for each playlist
                    video_data = self.youtube_client.get_videos(playlist_info.get("id"))
                    for video_info in video_data:
                        self.mongo_handler.insert_video(json_to_dict(video_info))
                        # st.write(f"video_info : {type(json_to_dict(video_info))}")

                        try:
                            # Fetch comments for each video
                            comment_data = self.youtube_client.get_comments(video_info['contentDetails']['videoId'])
                            for comment_info in comment_data:
                                self.mongo_handler.insert_comment(json_to_dict(comment_info))
                                # st.write(f"comment_info : {type(json_to_dict(comment_info))}")
                        except HttpError as http_error:
                            # Extract and log simplified error information
                            error_details = json.loads(http_error.content.decode())
                            video_id = video_info['contentDetails']['videoId']
                            reason = next(
                                (error['reason'] for error in error_details.get('error', {}).get('errors', []) if
                                 'reason' in error), 'Unknown reason')
                            st.write(f"Error fetching comments for videoId '{video_id}': reason: '{reason}'")
                        except Exception as e:
                            st.write(f"Error fetching or inserting comments for video {video_info['contentDetails']['videoId']}: {e}")
                except Exception as e:
                    st.write(f"Error fetching or inserting videos for playlist {playlist_info.get('id')}: {e}")
        except Exception as e:
            st.write(f"Error fetching or inserting playlists for channel {channel_id}: {e}")

    def render(self):
        # Front page
        st.title('Channel ID Manager')

        # Text input and add button
        channel_id_input = st.text_input('Enter Channel ID:', value=st.session_state.new_channel_id)
        if st.button('Add'):
            self.add_channel_id(channel_id_input)

        # Display the table with delete buttons
        if not st.session_state.channels.empty:
            st.write('Channel IDs Table:')
            df = st.session_state.channels.copy()

            for i, (index, row) in enumerate(df.iterrows()):
                col1, col2 = st.columns([5, 2])
                with col1:
                    st.write(row['Channel ID'])
                with col2:
                    if st.button(f'Delete', key=f'delete_{index}'):
                        self.delete_channel_id(self, index)
                        st.rerun()

            # Add a fetch button to display all channel IDs
            if st.button('Fetch'):
                for index, row in st.session_state.channels.iterrows():
                    channel_id = row['Channel ID']
                    try:
                        # Fetch data from YouTube and insert into MongoDB
                        self.fetch_data_from_source(channel_id)
                        st.success(f"Successfully inserted channel {channel_id}")
                    except Exception as e:
                        st.error(f"Error fetching or inserting channel {channel_id}: {e}")
        else:
            st.write('No channel IDs added yet.')


# Create an instance of the app and render it
app = ChannelIDManagerApp()
app.render()
