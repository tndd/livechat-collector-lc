from dataclasses import dataclass
from typing import List
from mysql.connector.cursor_cext import CMySQLCursor

from service.database.db import mysql_query


@dataclass
class VideoDBClient:
    @staticmethod
    @mysql_query
    def insert_rows_into_video_table(
            cursor: CMySQLCursor,
            rows_data: List[tuple]
    ) -> None:
        query = """
        INSERT IGNORE INTO livechat_collector.video(
            id,
            channel_id,
            published_at,
            title,
            view_count,
            like_count,
            dislike_count
        )
        VALUES(%s, %s, %s, %s, %s, %s, %s);
        """
        cursor.executemany(query, rows_data)

    @staticmethod
    @mysql_query
    def insert_rows_into_video_collaborated_channel_ids_table(
            cursor: CMySQLCursor,
            rows_data: List[tuple]
    ) -> None:
        query = """
        INSERT IGNORE INTO livechat_collector.video_collaborated_channel_id (
            video_id,
            collaborated_id
        ) VALUES(%s, %s);
        """
        cursor.executemany(query, rows_data)
