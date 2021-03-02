import os

from dataclasses import dataclass
from datetime import datetime
from typing import List
from dotenv import load_dotenv

from service.client.video_db_client import VideoDBClient
from service.client.y_initial_data_client import YInitialDataClient
from service.client.youtube_data_api_client import YoutubeDataAPIClient
from repository.channel import ChannelRepository
from service.client.table.video_row import VideoRow

# TODO: tmp
from youtube_data_api import load_youtube_data_api_search_list

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
    @staticmethod
    def store_video_rows_of_channel_id(channel_id: str) -> None:
        file_path = f"data/youtube_data_api/search/{channel_id}.json"
        if os.path.exists(file_path):
            video_rows = YoutubeDataAPIClient.read_video_rows_from_file(file_path)
        else:
            video_rows = YoutubeDataAPIClient.get_video_rows_from_channel_id(channel_id)
        query_params = list(map(lambda vr: vr.to_param(), video_rows))
        VideoDBClient.insert_rows_into_video_table(query_params)

    @classmethod
    def load_all_channel_video_rows_into_db(cls) -> None:
        channel_ids = ChannelRepository.get_channel_ids()
        for cid in channel_ids:
            cls.store_video_rows_of_channel_id(cid)

    @staticmethod
    def get_video_row_from_video_id(video_id: str) -> VideoRow:
        row = VideoDBClient.select_row_from_video_table(video_id)
        return VideoRow(
            id=row[0],
            channel_id=row[1],
            published_at=row[2],
            title=row[3],
        )

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
        for idx, search_data in enumerate(search_list):
            video_id = search_data['id']['videoId']
            print(f"[{idx + 1}/{len(search_list)}]: {video_id}")
            y_initial_data_obj = YInitialDataClient.get_y_initial_data_obj_from_video_id(video_id)
            # TODO remove
            # y_initial_data = YInitialDataRepository.load_y_initial_data_from_video_id(video_id)
            # y_initial_data_obj = YInitialDataClient.from_y_initial_data_dict_to_obj(y_initial_data)
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
