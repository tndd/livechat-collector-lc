import os

from service.client.video_db_client import VideoDBClient, VideoData, VideoStatisticsData
from service.client.youtube_data_api_client import YoutubeDataAPIClient
from service.client.y_initial_data_client import YInitialDataClient
from repository.channel import ChannelRepository


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

    @staticmethod
    def store_video_statistics_of_video_id(video_id: str) -> None:
        y_initial_data_result = YInitialDataClient.get_from_video_id(video_id)
        video_statistics_data = VideoStatisticsData(
            video_id=y_initial_data_result.video_id,
            view_count=y_initial_data_result.view_count,
            like_count=y_initial_data_result.like_count,
            dislike_count=y_initial_data_result.dislike_count
        )
        VideoDBClient.insert_video_statistics(video_statistics_data)

    @classmethod
    def load_all_channel_videos_data_into_db(cls) -> None:
        channel_ids = ChannelRepository.get_channel_ids()
        for cid in channel_ids:
            cls.store_videos_data_of_channel_id(cid)
