import json

from typing import List
from dataclasses import dataclass

from service.client.channel_db_client import ChannelDBClient, ChannelData


@dataclass
class Channel:
    id: str
    code: str
    name: str
    group: List[str]


class ChannelRepository:
    @classmethod
    def load_channels_data_into_db_from_file(
            cls,
            file_path='./channel.json') -> None:
        with open(file_path, 'r') as f:
            channels_dict = json.load(f)
        channels_data = []
        for code, data in channels_dict.items():
            channels_data.append(
                ChannelData(
                    id=data['id'],
                    code=code,
                    name=data['name']
                )
            )
        ChannelDBClient.insert_channels_data(channels_data)

    @classmethod
    def get_channels(cls) -> List[Channel]:
        channels_data = ChannelDBClient.select_channels_data()
        return list(map(lambda cd: (
            Channel(
                id=cd.id,
                code=cd.code,
                name=cd.name,
                group=[]
            )
        ), channels_data))

    @classmethod
    def get_channel_ids(cls) -> List[str]:
        return list(map(lambda c: c.id, cls.get_channels()))
