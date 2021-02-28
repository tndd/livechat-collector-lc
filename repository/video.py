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
from service.client.database.video_db_client import VideoDBClient
from service.client.crawler.y_initial_data_client import YInitialDataClient

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

    @classmethod
    def get_video_model_from_id(cls, video_id: str) -> VideoModel:
        row = VideoDBClient.select_row_from_video_table(video_id)
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
    def get_video_models_from_channel_id(cls, channel_id: str) -> List[VideoModel]:
        # TODO: tmp
        # search_list = cls.get_channel_search_list_from_channel_id(channel_id)
        search_list = load_youtube_data_api_search_list(channel_id)
        video_models = []
        for search_data in search_list:
            video_id = search_data['id']['videoId']
            # y_initial_data_obj = YInitialDataClient.get_y_initial_data_obj_from_video_id(video_id)
            # TODO remove
            y_initial_data = YInitialDataRepository.load_y_initial_data_from_video_id(video_id)
            y_initial_data_obj = YInitialDataClient.from_y_initial_data_dict_to_obj(y_initial_data)
            ###
            video_models.append(
                VideoModel(
                    id=video_id,
                    channel_id=channel_id,
                    published_at=datetime.strptime(search_data['snippet']['publishedAt'], '%Y-%m-%dT%H:%M:%SZ'),
                    title=search_data['snippet']['title'],
                    view_count=y_initial_data_obj.view_count,
                    like_count=y_initial_data_obj.like_count,
                    dislike_count=y_initial_data_obj.dislike_count,
                    collaborated_channel_ids=[x for x in y_initial_data_obj.collaborated_channel_ids if x != channel_id]
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
