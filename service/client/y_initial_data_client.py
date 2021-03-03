import requests
import re
import json

from typing import List
from bs4 import BeautifulSoup
from dataclasses import dataclass


@dataclass
class YInitialDataResult:
    video_id: str
    view_count: int
    like_count: int
    dislike_count: int
    collaborated_channel_ids: List[str]


class NotFoundYInitialDataError(Exception):
    pass


class YInitialDataClient:
    @staticmethod
    def get_url_of_video_id(video_id: str) -> str:
        return f"https://www.youtube.com/watch?v={video_id}"

    @classmethod
    def get_y_initial_data_from_video_id(cls, video_id: str) -> dict:
        r = requests.get(cls.get_url_of_video_id(video_id))
        soup = BeautifulSoup(r.text, 'lxml')
        for element in soup.find_all('script'):
            content = str(element.string)
            if re.match(r'^(var ytInitialData = )', content):
                y_initial_data = content[len('var ytInitialData = '):-len(';')]
                return json.loads(y_initial_data)
        raise NotFoundYInitialDataError(f"Not found y_initial_data: {video_id}")

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
            channel_ids: List[str]
    ) -> List[str]:
        description_data = \
            y_initial_data['contents']['twoColumnWatchNextResults']['results']['results']['contents'][1][
                'videoSecondaryInfoRenderer']['description']['runs']
        description_text = json.dumps(description_data)
        collaborated_ids = []
        for channel_id in channel_ids:
            if channel_id in description_text:
                collaborated_ids.append(channel_id)
        return collaborated_ids

    @classmethod
    def get_from_video_id(cls, video_id: str, channel_ids: List[str]) -> YInitialDataResult:
        y_initial_data = cls.get_y_initial_data_from_video_id(video_id)
        return YInitialDataResult(
            video_id=video_id,
            view_count=cls.extract_view_count_from_y_initial_data(y_initial_data),
            like_count=cls.extract_like_count_from_y_initial_data(y_initial_data),
            dislike_count=cls.extract_dislike_count_from_y_initial_data(y_initial_data),
            collaborated_channel_ids=cls.extract_collaborated_channel_ids_from_y_initial_data(
                y_initial_data,
                channel_ids
            )
        )
