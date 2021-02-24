import json
import os
import requests
import re

from dataclasses import dataclass
from typing import Optional, List
from bs4 import BeautifulSoup

from youtube_data_api import get_video_ids_from_channel_id
from repository.channel import ChannelRepository


@dataclass
class YInitialDataRepository:
    y_initial_data_dir_path: str = './data/y_initial_data'

    @classmethod
    def get_path_y_initial_data_file(cls, video_id: str) -> str:
        return f"{cls.y_initial_data_dir_path}/{video_id}.json"

    @classmethod
    def is_exist_y_initial_data(cls, video_id: str) -> bool:
        return os.path.exists(cls.get_path_y_initial_data_file(video_id))

    @classmethod
    def clear_y_initial_data(cls, video_id: str) -> None:
        if cls.is_exist_y_initial_data(video_id):
            os.remove(cls.get_path_y_initial_data_file(video_id))

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

    @classmethod
    def store_y_initial_data(cls, video_id: str, y_initial_data: dict) -> None:
        with open(cls.get_path_y_initial_data_file(video_id), 'w') as f:
            json.dump(y_initial_data, f, ensure_ascii=False, indent=4)
        print(f"[STORED]: Y_INITIAL_DATA \"{video_id}\"")

    @classmethod
    def download_y_initials_data_from_channel_id(cls, channel_id: str) -> None:
        video_ids = get_video_ids_from_channel_id(channel_id)  # TODO: "video_ids" will get from VideoDataRepository
        for video_id in video_ids:
            if cls.is_exist_y_initial_data(video_id):
                print(f"[SKIP]: Y_INITIAL_DATA \"{video_id}\" have already been downloaded.")
                continue
            try:
                y_initial_data = cls.get_y_initial_data_from_video_id(video_id)
                cls.store_y_initial_data(video_id, y_initial_data)
            except Exception as e:
                cls.clear_y_initial_data(video_id)
                print(f"[ERROR]: Download Y_INITIAL_DATA \"{video_id}\" is missed.")
        print(f"[Completed]: Y_INITIALS_DATA of \"{channel_id}\"")

    @classmethod
    def load_y_initial_data_from_video_id(cls, video_id: str) -> dict:
        with open(cls.get_path_y_initial_data_file(video_id), 'r') as f:
            y_initial_data = json.load(f)
        return y_initial_data

    @staticmethod
    def extract_collaborated_ids_from_y_initial_data(y_initial_data: dict) -> List[str]:
        contents = y_initial_data['contents']['twoColumnWatchNextResults']['results']['results']['contents']
        for content in contents:
            if 'videoSecondaryInfoRenderer' in content.keys():
                description_data = content['videoSecondaryInfoRenderer']['description']['runs']
                print(description_data)

    @classmethod
    def extract_video_data_from_y_initial_data(cls, y_initial_data) -> dict:
        # collaborated_ids
        ids = ChannelRepository.get_channel_ids()
        print(ids)
        # time_length
        # view_count
        # like_count
        # dislike_count
        pass

