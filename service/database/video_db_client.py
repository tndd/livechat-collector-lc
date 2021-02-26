from dataclasses import dataclass
from typing import List
from mysql.connector.cursor_cext import CMySQLCursor

from service.database.db import mysql_query


@dataclass
class VideoDBClient:
    @staticmethod
    @mysql_query
    def insert_rows(
            cursor: CMySQLCursor,
            rows_data: List[tuple]
    ):
        query = """
        INSERT INTO livechat_collector.video(
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
