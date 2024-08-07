from googleapiclient.discovery import build

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
        return response
