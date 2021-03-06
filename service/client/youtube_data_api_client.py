import os
import json

import googleapiclient.discovery

from typing import Optional, Tuple, List
from datetime import datetime
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv('.env')


@dataclass
class YoutubeDataAPiResult:
    id: str
    channel_id: str
    published_at: datetime
    title: str

    def to_param(self) -> tuple:
        return (
            self.id,
            self.channel_id,
            self.published_at.strftime('%Y-%m-%d %H:%M:%S'),
            self.title
        )


class YoutubeDataAPIClient:
    @staticmethod
    def get_youtube_api_client():
        api_service_name = "youtube"
        api_version = "v3"
        api_key = os.environ.get("YOUTUBE_DATA_API_KEY")

        youtube_api_client = googleapiclient.discovery.build(
            api_service_name,
            api_version,
            developerKey=api_key
        )
        return youtube_api_client

    @classmethod
    def get_channel_search_list_from_channel_id_part(
            cls,
            channel_id: str,
            next_page_token: Optional[str] = None
    ) -> Tuple[str, dict]:
        youtube_api_client = cls.get_youtube_api_client()
        request = youtube_api_client.search().list(
            part="snippet",
            channelId=channel_id,
            eventType="completed",
            maxResults=50,
            order="date",
            type="video",
            pageToken=next_page_token
        )
        response = request.execute()

        return response.get('nextPageToken', 'EMPTY'), response['items']

    @classmethod
    def get_channel_search_list_from_channel_id(cls, channel_id: str) -> List[dict]:
        next_page_token = None
        search_list = []
        while next_page_token != 'EMPTY':
            next_page_token, search_list_part = cls.get_channel_search_list_from_channel_id_part(
                channel_id,
                next_page_token
            )
            search_list.extend(search_list_part)
        print(f"[Downloaded]: SEARCH_LIST \"{channel_id}\"")
        return search_list

    @staticmethod
    def convert_search_list_to_results(search_list: List[dict]) -> List[YoutubeDataAPiResult]:
        return list(map(lambda d: (
            YoutubeDataAPiResult(
                id=d['id']['videoId'],
                channel_id=d['snippet']['channelId'],
                published_at=datetime.strptime(d['snippet']['publishedAt'], '%Y-%m-%dT%H:%M:%SZ'),
                title=d['snippet']['title']
            )
        ), search_list))

    @classmethod
    def get_from_channel_id(cls, channel_id: str) -> List[YoutubeDataAPiResult]:
        search_list = cls.get_channel_search_list_from_channel_id(channel_id)
        return cls.convert_search_list_to_results(search_list)

    @classmethod
    def read_from_file(cls, file_path: str) -> List[YoutubeDataAPiResult]:
        # this is a temporary method. so it will be removed.
        with open(file_path, 'r') as f:
            search_list = json.load(f)
        return cls.convert_search_list_to_results(search_list)
