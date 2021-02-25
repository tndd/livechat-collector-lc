import os
import requests
import re
import json

import googleapiclient.discovery
import mysql.connector as mysql

from dataclasses import dataclass
from typing import Optional, Tuple, List
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from repository.channel import ChannelRepository


load_dotenv('.env')


@dataclass
class VideoModel:
    id: str
    channel_id: str
    published_at: str
    title: str
    view_count: int
    like_count: int
    dislike_count: int
    collaborated_ids: List[str]


class VideoRepository:
    dir_path_video: str = './data/video'

    @classmethod
    def get_file_path_video(cls, channel_id: str) -> str:
        return f"{cls.dir_path_video}/{channel_id}.json"

    @classmethod
    def is_exist_file_video_id(cls, channel_id: str) -> bool:
        return os.path.exists(cls.get_file_path_video(channel_id))

    @classmethod
    def clear_video(cls, channel_id: str) -> None:
        if cls.is_exist_file_video_id(channel_id):
            os.remove(cls.get_file_path_video(channel_id))

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
    def get_url_of_video_id(video_id: str) -> str:
        return f"https://www.youtube.com/watch?v={video_id}"

    @classmethod
    def get_y_initial_data_from_video_id(cls, video_id: str) -> Optional[dict]:
        r = requests.get(cls.get_url_of_video_id(video_id))
        soup = BeautifulSoup(r.text, 'lxml')
        for element in soup.find_all('script'):
            content = str(element.string)
            if re.match(r'^(var ytInitialData = )', content):
                y_initial_data = content[len('var ytInitialData = '):-len(';')]
                return json.loads(y_initial_data)
        return None

    @staticmethod
    def extract_view_count_from_y_initial_data(y_initial_data: dict) -> int:
        view_count_text = y_initial_data['contents']['twoColumnWatchNextResults']['results']['results']['contents'][0]['videoPrimaryInfoRenderer']['viewCount']['videoViewCountRenderer']['viewCount']['simpleText']
        view_count = re.sub("\\D", "", view_count_text)
        return int(view_count)

    @staticmethod
    def extract_like_count_from_y_initial_data(y_initial_data: dict) -> int:
        like_count_text = \
            y_initial_data['contents']['twoColumnWatchNextResults']['results']['results']['contents'][0][
                'videoPrimaryInfoRenderer']['videoActions']['menuRenderer']['topLevelButtons'][0][
                'toggleButtonRenderer']['defaultText']['simpleText']
        like_count = re.sub("\\D", "", like_count_text)
        return int(like_count)

    @staticmethod
    def extract_dislike_count_from_y_initial_data(y_initial_data: dict) -> int:
        dislike_count_text = \
            y_initial_data['contents']['twoColumnWatchNextResults']['results']['results']['contents'][0][
                'videoPrimaryInfoRenderer']['videoActions']['menuRenderer']['topLevelButtons'][1][
                'toggleButtonRenderer']['defaultText']['simpleText']
        like_count = re.sub("\\D", "", dislike_count_text)
        return int(like_count)

    @staticmethod
    def extract_collaborated_ids_from_y_initial_data(y_initial_data: dict) -> List[str]:
        description_data = y_initial_data['contents']['twoColumnWatchNextResults']['results']['results']['contents'][1]['videoSecondaryInfoRenderer']['description']['runs']
        description_text = json.dumps(description_data)
        collaborated_ids = []
        for channel_id in ChannelRepository.get_channel_ids():
            if channel_id in description_text:
                collaborated_ids.append(channel_id)
        return collaborated_ids

    @classmethod
    def get_videos_from_channel_id(cls, channel_id: str) -> List[VideoModel]:
        search_list = cls.get_channel_search_list_from_channel_id(channel_id)
        video_models = []
        for search_data in search_list:
            y_initial_data = cls.get_y_initial_data_from_video_id(search_data['id']['videoId'])
            video_models.append(
                VideoModel(
                    id=search_data['id']['videoId'],
                    channel_id=search_data['snippet']['channelId'],
                    published_at=search_data['snippet']['publishedAt'],
                    title=search_data['snippet']['title'],
                    view_count=cls.extract_view_count_from_y_initial_data(y_initial_data),
                    like_count=cls.extract_like_count_from_y_initial_data(y_initial_data),
                    dislike_count=cls.extract_dislike_count_from_y_initial_data(y_initial_data),
                    collaborated_ids=cls.extract_collaborated_ids_from_y_initial_data(y_initial_data)
                )
            )
        return video_models

    @staticmethod
    def get_mysql_client():
        connection = mysql.connect(
            host=os.environ.get('MYSQL_HOST'),
            port=os.environ.get('MYSQL_PORT'),
            user=os.environ.get('MYSQL_USER'),
            password=os.environ.get('MYSQL_PASSWORD'),
            database=os.environ.get('MYSQL_DB_NAME'),
        )
        return connection

    @classmethod
    def store_video_model_into_db(cls, video_model: VideoModel) -> None:
        pass  # TODO

    @classmethod
    def store_video_models_into_db(cls, video_models: List[VideoModel]) -> None:
        pass  # TODO
