from dataclasses import dataclass
from typing import List
from mysql.connector.cursor_cext import CMySQLCursor

from service.client.db import mysql_query
from service.client.table.video_row import VideoRow


@dataclass
class VideoDBClient:
    @staticmethod
    @mysql_query
    def insert_rows_into_video_table(
            cursor: CMySQLCursor,
            rows_data: List[tuple]) -> None:
        query = """
        INSERT IGNORE INTO livechat_collector.video(
            id,
            channel_id,
            published_at,
            title
        )
        VALUES(%s, %s, %s, %s);
        """
        cursor.executemany(query, rows_data)

    @staticmethod
    @mysql_query
    def select_row_from_video_table(
            cursor: CMySQLCursor,
            video_id: str) -> VideoRow:
        query = """
        SELECT id, channel_id, published_at, title
        FROM livechat_collector.video
        WHERE id = %s;
        """
        cursor.execute(query, (video_id,))
        return cursor.fetchone()

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
