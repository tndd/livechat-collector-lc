from dataclasses import dataclass
from typing import List
from mysql.connector.cursor_cext import CMySQLCursor

from service.db import mysql_query
from model.table.video_data import VideoData


@dataclass
class VideoDBClient:
    @staticmethod
    @mysql_query
    def insert_videos_data_into_video_table(
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
        rows_data = list(map(lambda vd: vd.to_row_video_table(), videos_data))
        cursor.executemany(query, rows_data)

    @staticmethod
    @mysql_query
    def select_video_data_from_video_table(
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
            title=row[3],
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
