from typing import List
from mysql.connector.cursor_cext import CMySQLCursor

from service.db import mysql_query
from service.client.table.channel_data import ChannelData


class ChannelDBClient:
    @staticmethod
    @mysql_query
    def insert_channels_data_into_channel_table(
        cursor: CMySQLCursor,
        channels_data: List[ChannelData]
    ) -> None:
        query = '''
        INSERT IGNORE INTO livechat_collector.channel (id, code, name) 
        VALUES(%s, %s, %s);
        '''
        rows_data = list(map(lambda cm: cm.to_channel_table_row(), channels_data))
        cursor.executemany(query, rows_data)

    @staticmethod
    @mysql_query
    def select_channels_data(
            cursor: CMySQLCursor
    ) -> List[ChannelData]:
        query = '''
        SELECT id, code, name FROM livechat_collector.channel;
        '''
        cursor.execute(query)
        rows = cursor.fetchall()
        channels_data = list(map(lambda r: ChannelData(
            id=r[0],
            code=r[1],
            name=r[2]
        ), rows))
        return channels_data
