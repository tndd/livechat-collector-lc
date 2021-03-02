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
class VideoDBClient:
    @staticmethod
    @mysql_query
    def insert_videos_data(
            cursor: CMySQLCursor,
            videos_data: List[tuple]) -> None:
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

    @staticmethod
    @mysql_query
    def insert_rows_into_video_collaborated_channel_ids_table(
            cursor: CMySQLCursor,
            rows_data: List[tuple]
    ) -> None:
        query = """
        INSERT IGNORE INTO livechat_collector.video_collaborated_channel_id (
            video_id,
            collaborated_channel_id
        ) VALUES(%s, %s);
        """
        cursor.executemany(query, rows_data)
