import os

from typing import List
from dataclasses import dataclass
from datetime import datetime

from service.client.video_db_client import VideoDBClient, VideoData, VideoStatisticsData, VideoCollaboratedChannelId
from service.client.youtube_data_api_client import YoutubeDataAPIClient
from service.client.y_initial_data_client import YInitialDataClient
from repository.channel import ChannelRepository


@dataclass
class Video:
    id: str
    channel_id: str
    published_at: datetime
    title: str
    view_count: int
    like_count: int
    dislike_count: int
    collaborated_channel_ids: List[str]


class VideoRepository:
    @staticmethod
    def store_videos_data_of_channel_id(channel_id: str) -> None:
        file_path = f"data/youtube_data_api/search/{channel_id}.json"
        if os.path.exists(file_path):
            youtube_data_api_results = YoutubeDataAPIClient.read_from_file(file_path)
        else:
            youtube_data_api_results = YoutubeDataAPIClient.get_from_channel_id(channel_id)
        videos_data = list(map(lambda r: VideoData(
            id=r.id,
            channel_id=r.channel_id,
            published_at=r.published_at,
            title=r.title
        ), youtube_data_api_results))
        VideoDBClient.insert_videos_data(videos_data)

    @classmethod
    def store_y_initial_data_of_video_id(cls, video_id: str) -> None:
        if VideoDBClient.select_video_statistics_of_video_id(video_id) is not None:
            print(f"video_id: {video_id} is already exist in db.")
            return
        y_initial_data_result = YInitialDataClient.get_from_video_id(video_id)
        video_statistics = VideoStatisticsData(
            video_id=y_initial_data_result.video_id,
            view_count=y_initial_data_result.view_count,
            like_count=y_initial_data_result.like_count,
            dislike_count=y_initial_data_result.dislike_count
        )
        channel_ids = ChannelRepository.get_channel_ids()
        self_channel_id = VideoRepository.get_channel_id_of_video(video_id)
        video_collaborated_channel_ids = list(map(lambda cid: VideoCollaboratedChannelId(
            video_id=video_id,
            channel_id=cid
        ), y_initial_data_result.collaborated_channel_ids(channel_ids, self_channel_id)))
        VideoDBClient.insert_video_statistics(video_statistics)
        VideoDBClient.insert_video_collaborated_channel_ids(video_collaborated_channel_ids)

    @classmethod
    def load_all_channel_videos_data_into_db(cls) -> None:
        channel_ids = ChannelRepository.get_channel_ids()
        for cid in channel_ids:
            cls.store_videos_data_of_channel_id(cid)

    @classmethod
    def load_y_initial_data_list_result_of_channel_id_into_db(cls, channel_id: str):
        video_ids = cls.get_video_ids_of_channel_id(channel_id)
        for video_id in video_ids:
            print(video_id)
            try:
                cls.store_y_initial_data_of_video_id(video_id)
            except Exception:
                print(f"skipped")
                continue

    @classmethod
    def load_channels_into_db(cls) -> None:
        cls.load_all_channel_videos_data_into_db()
        channel_ids = ChannelRepository.get_channel_ids()
        for cid in channel_ids:
            print(cid)
            cls.load_y_initial_data_list_result_of_channel_id_into_db(cid)

    @staticmethod
    def get_channel_id_of_video(video_id: str) -> str:
        video_data = VideoDBClient.select_video_data_from_video_id(video_id)
        return video_data.channel_id

    @staticmethod
    def get_video_ids_of_channel_id(channel_id: str) -> List[str]:
        videos_data = VideoDBClient.select_videos_data_of_channel_id(channel_id)
        return list(map(lambda vd: vd.id, videos_data))
