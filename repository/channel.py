import json

from dataclasses import dataclass
from typing import List

from service.client.channel_db_client import ChannelDBClient
from service.client.video_db_client import VideoDBClient
from model.channel import ChannelModel


@dataclass
class ChannelRepository:
    @classmethod
    def load_channels_data_from_file(cls, path) -> dict:
        with open(path, 'r') as f:
            channels_data = json.load(f)
        return channels_data

    @staticmethod
    def store_channel_models_into_db(channels: List[ChannelModel]) -> None:
        rows_data = list(map(lambda cm: cm.to_channel_table_row(), channels))
        ChannelDBClient.insert_rows_into_channel_table(rows_data)

    @classmethod
    def load_channel_models_into_db_from_file(cls) -> None:
        channels_data = cls.load_channels_data_from_file('./channel.json')
        channel_models = []
        for code, data in channels_data.items():
            channel_models.append(
                ChannelModel(
                    id=data['id'],
                    code=code,
                    name=data['name']
                )
            )
        cls.store_channel_models_into_db(channel_models)

    @classmethod
    def get_all_channel_models(cls) -> List[ChannelModel]:
        rows_data = ChannelDBClient.select_rows_from_channel_table()
        channel_models = list(map(lambda r: ChannelModel(
            id=r[0],
            code=r[1],
            name=r[2]
        ), rows_data))
        return channel_models

    @classmethod
    def get_all_channel_ids(cls) -> List[str]:
        channel_models = cls.get_all_channel_models()
        channel_ids = []
        for channel_model in channel_models:
            channel_ids.append(channel_model.id)
        return channel_ids
