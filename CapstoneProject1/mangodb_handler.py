from pymongo import MongoClient, errors
from typing import Dict, Any, List


class MongoDBHandler:
    def __init__(self, uri: str, db_name: str):
        self.client = MongoClient(uri)
        self.db = self.client[db_name]

    def insert_document(self, collection_name: str, document: Dict[str, Any]) -> str:
        collection = self.db[collection_name]

        try:
            # Insert the new document
            result = collection.insert_one(document)
            return str(result.inserted_id)

        except errors.DuplicateKeyError:
            # Handle duplicate etag error
            existing_document = collection.find_one({'etag': document.get('etag')})
            if existing_document:
                return str(existing_document['_id'])
            else:
                # Unexpected error occurred, re-raise
                raise

    def get_documents(self, collection_name: str, query: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        if query is None:
            query = {}
        collection = self.db[collection_name]
        documents = collection.find(query)
        return list(documents)

    def insert_channel(self, channel: Dict[str, Any]) -> str:
        return self.insert_document("channels", channel)

    def insert_playlist(self, playlist: Dict[str, Any]) -> str:
        return self.insert_document("playlists", playlist)

    def insert_video(self, video: Dict[str, Any]) -> str:
        return self.insert_document("videos", video)

    def insert_comment(self, comment: Dict[str, Any]) -> str:
        return self.insert_document("comments", comment)

    def get_channels(self, query: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        return self.get_documents("channels", query)

    def get_playlists(self, query: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        return self.get_documents("playlists", query)

    def get_videos(self, query: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        return self.get_documents("videos", query)

    def get_comments(self, query: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        return self.get_documents("comments", query)