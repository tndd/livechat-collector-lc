from typing import List
from mysql.connector.cursor_cext import CMySQLCursor

from service.db import mysql_query


class ChannelDBClient:
    @staticmethod
    @mysql_query
    def insert_rows_into_channel_table(
        cursor: CMySQLCursor,
        rows_data: List[tuple]
    ) -> None:
        query = '''
        INSERT IGNORE INTO livechat_collector.channel (id, code, name) 
        VALUES(%s, %s, %s);
        '''
        cursor.executemany(query, rows_data)