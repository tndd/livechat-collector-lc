import os
import requests
import re
import json

import googleapiclient.discovery

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple, List
from bs4 import BeautifulSoup
from dotenv import load_dotenv

from repository.channel import ChannelRepository
from service.database.video_db_client import VideoDBClient

# TODO: tmp
from youtube_data_api import load_youtube_data_api_search_list
from repository.y_initial_data import YInitialDataRepository

load_dotenv('.env')


@dataclass
class VideoModel:
    id: str
    channel_id: str
    published_at: datetime
    title: str
    view_count: int
    like_count: int
    dislike_count: int
    collaborated_channel_ids: List[str]

    def to_row_data_video_table(self) -> tuple:
        return (
            self.id,
            self.channel_id,
            self.published_at.strftime('%Y-%m-%d %H:%M:%S'),
            self.title,
            self.view_count,
            self.like_count,
            self.dislike_count
        )

    def to_rows_data_video_collaborated_table(self) -> List[tuple]:
        return list(map(
            lambda channel_id: (self.id, channel_id),
            self.collaborated_channel_ids)
        )


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
    def get_video_model_from_id(cls, video_id: str) -> Optional[VideoModel]:
        row = VideoDBClient.select_row_video_table(video_id)
        return VideoModel(
            id=row[0],
            channel_id=row[1],
            published_at=row[2],
            title=row[3],
            view_count=row[4],
            like_count=row[5],
            dislike_count=row[6],
            collaborated_channel_ids=[]  # TODO
        )

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
        view_count_text = \
            y_initial_data['contents']['twoColumnWatchNextResults']['results']['results']['contents'][0][
                'videoPrimaryInfoRenderer']['viewCount']['videoViewCountRenderer']['viewCount']['simpleText']
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
    def extract_collaborated_channel_ids_from_y_initial_data(
            y_initial_data: dict,
            self_channel_id: str) -> List[str]:
        description_data = \
            y_initial_data['contents']['twoColumnWatchNextResults']['results']['results']['contents'][1][
                'videoSecondaryInfoRenderer']['description']['runs']
        description_text = json.dumps(description_data)
        collaborated_ids = []
        for channel_id in ChannelRepository.get_channel_ids():
            if channel_id in description_text:
                collaborated_ids.append(channel_id)
        return [x for x in collaborated_ids if x != self_channel_id]

    @classmethod
    def get_video_models_from_channel_id(cls, channel_id: str) -> List[VideoModel]:
        # TODO: tmp
        # search_list = cls.get_channel_search_list_from_channel_id(channel_id)
        search_list = load_youtube_data_api_search_list(channel_id)
        video_models = []
        for search_data in search_list:
            # TODO: tmp
            # y_initial_data = cls.get_y_initial_data_from_video_id(search_data['id']['videoId'])
            y_initial_data = YInitialDataRepository.load_y_initial_data_from_video_id(search_data['id']['videoId'])
            video_models.append(
                VideoModel(
                    id=search_data['id']['videoId'],
                    channel_id=search_data['snippet']['channelId'],
                    published_at=datetime.strptime(search_data['snippet']['publishedAt'], '%Y-%m-%dT%H:%M:%SZ'),
                    title=search_data['snippet']['title'],
                    view_count=cls.extract_view_count_from_y_initial_data(y_initial_data),
                    like_count=cls.extract_like_count_from_y_initial_data(y_initial_data),
                    dislike_count=cls.extract_dislike_count_from_y_initial_data(y_initial_data),
                    collaborated_channel_ids=cls.extract_collaborated_channel_ids_from_y_initial_data(
                        y_initial_data,
                        search_data['snippet']['channelId']
                    )
                )
            )
        return video_models

    @staticmethod
    def store_video_models(video_models: List[VideoModel]) -> None:
        records_video_table = list(map(lambda v: v.to_row_data_video_table(), video_models))
        VideoDBClient.insert_rows_into_video_table(records_video_table)
        for video in video_models:
            records_video_collaborated_channel_ids = video.to_rows_data_video_collaborated_table()
            VideoDBClient.insert_rows_into_video_collaborated_channel_ids_table(records_video_collaborated_channel_ids)
        return
