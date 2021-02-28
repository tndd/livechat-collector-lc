from typing import List
from mysql.connector.cursor_cext import CMySQLCursor

from service.client.database.db import mysql_query


class ChannelDBClient:
    @staticmethod
    @mysql_query
    def insert_rows(
        cursor: CMySQLCursor,
        rows_data: List[tuple]
    ) -> None:
        query = '''
        INSERT IGNORE INTO livechat_collector.channel (id, code, name) 
        VALUES(%s, %s, %s);
        '''
        cursor.executemany(query, rows_data)
