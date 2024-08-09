from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import logging

# Configure logging
logging.basicConfig(filename='errGoogleApiClient.log', level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class YouTubeClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)

    def get_channel_details(self, channel_id):
        request = self.youtube.channels().list(
            part='snippet,contentDetails,statistics',
            id=channel_id
        )
        response = request.execute()
        return response['items'][0] if response['items'] else None

    def get_playlists(self, channel_id):
        request = self.youtube.playlists().list(
            part='snippet,contentDetails',
            channelId=channel_id,
            maxResults=50
        )
        response = request.execute()
        return response['items']

    def get_videos(self, playlist_id):
        try:
            request = self.youtube.playlistItems().list(
                part='snippet,contentDetails',
                playlistId=playlist_id,
                maxResults=50
            )
            response = request.execute()
            return response['items']
        except HttpError as e:
            # Log the error details
            logging.error(f"HttpError 404 when requesting videos for playlistId {playlist_id}: {e}")
            # Optionally, you can raise the exception if you want to handle it further up the call stack
            raise

    def get_comments(self, video_id):
        request = self.youtube.commentThreads().list(
            part='snippet,replies',
            videoId=video_id,
            maxResults=100
        )
        response = request.execute()
        return response['items']
