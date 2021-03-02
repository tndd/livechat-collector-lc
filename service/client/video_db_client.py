from dataclasses import dataclass
from typing import List
from datetime import datetime
from mysql.connector.cursor_cext import CMySQLCursor

from service.client.db import mysql_query


@dataclass
class VideoData:
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


@dataclass
class VideoStatisticsData:
    video_id: str
    view_count: int
    like_count: int
    dislike_count: int

    def to_param(self) -> tuple:
        return (
            self.video_id,
            self.view_count,
            self.like_count,
            self.dislike_count
        )


@dataclass
class VideoCollaboratedChannelId:
    video_id: str
    channel_id: str

    def to_param(self) -> tuple:
        return (
            self.video_id,
            self.channel_id
        )


@dataclass
class VideoDBClient:
    @staticmethod
    @mysql_query
    def insert_videos_data(
            cursor: CMySQLCursor,
            videos_data: List[VideoData]) -> None:
        query = """
        INSERT IGNORE INTO livechat_collector.video(
            id,
            channel_id,
            published_at,
            title
        )
        VALUES(%s, %s, %s, %s);
        """
        rows_data = list(map(lambda vd: vd.to_param(), videos_data))
        cursor.executemany(query, rows_data)

    @staticmethod
    @mysql_query
    def insert_video_statistics(
            cursor: CMySQLCursor,
            video_statistics: VideoStatisticsData
    ) -> None:
        query = """
        INSERT IGNORE INTO livechat_collector.video_statistics (
            video_id,
            view_count,
            like_count,
            dislike_count
        ) VALUES(%s, %s, %s, %s);
        """
        cursor.execute(query, video_statistics.to_param())

    @staticmethod
    @mysql_query
    def insert_video_collaborated_channel_ids(
            cursor: CMySQLCursor,
            video_collaborated_channel_ids: List[VideoCollaboratedChannelId]
    ) -> None:
        query = """
        INSERT IGNORE INTO livechat_collector.video_collaborated_channel_id (
            video_id,
            collaborated_channel_id
        ) VALUES(%s, %s);
        """
        rows_data = list(map(lambda x: x.to_param(), video_collaborated_channel_ids))
        cursor.executemany(query, rows_data)

    @staticmethod
    @mysql_query
    def select_video_data_from_video_id(
            cursor: CMySQLCursor,
            video_id: str) -> VideoData:
        query = """
        SELECT id, channel_id, published_at, title
        FROM livechat_collector.video
        WHERE id = %s;
        """
        cursor.execute(query, (video_id,))
        row = cursor.fetchone()
        return VideoData(
            id=row[0],
            channel_id=row[1],
            published_at=row[2],
            title=row[3]
        )
