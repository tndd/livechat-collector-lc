from typing import List
from dataclasses import dataclass
from mysql.connector.cursor_cext import CMySQLCursor

from service.client.db import mysql_query


@dataclass
class ChannelData:
    id: str
    code: str
    name: str

    def to_param(self) -> tuple:
        return self.id, self.code, self.name


class ChannelDBClient:
    @staticmethod
    @mysql_query
    def insert_channels_data(
        cursor: CMySQLCursor,
        channels_data: List[ChannelData]
    ) -> None:
        query = '''
        INSERT IGNORE INTO livechat_collector.channel (id, code, name) 
        VALUES(%s, %s, %s);
        '''
        rows_data = list(map(lambda cd: cd.to_param(), channels_data))
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
