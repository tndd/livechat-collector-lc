import json

from dataclasses import dataclass
from typing import List

from service.client.channel_db_client import ChannelDBClient
from model.channel import ChannelModel


@dataclass
class ChannelRepository:
    channel_file_path = './channel.json'

    @classmethod
    def load_channels_data(cls) -> dict:
        with open(cls.channel_file_path, 'r') as f:
            channels_data = json.load(f)
        return channels_data

    @staticmethod
    def conversion_channel_data_to_model(
            channel_code: str,
            channel_data: dict
    ) -> ChannelModel:
        return ChannelModel(
            id=channel_data['id'],
            code=channel_code,
            name=channel_data['name']
        )

    @classmethod
    def load_channel_models_from_json(cls) -> List[ChannelModel]:
        channels_data = cls.load_channels_data()
        channel_models = []
        for code, data in channels_data.items():
            channel_models.append(cls.conversion_channel_data_to_model(code, data))
        return channel_models

    @classmethod
    def get_channel_ids(cls) -> List[str]:
        channel_models = cls.load_channel_models_from_json()
        channel_ids = []
        for channel_model in channel_models:
            channel_ids.append(channel_model.id)
        return channel_ids

    @staticmethod
    def store_channel_models_into_db(channels: List[ChannelModel]) -> None:
        rows_data = list(map(lambda cm: cm.to_channel_table_row(), channels))
        ChannelDBClient.insert_rows_into_channel_table(rows_data)

    @classmethod
    def load_rows_into_db_from_json(cls) -> None:
        channel_models = cls.load_channel_models_from_json()
        cls.store_channel_models_into_db(channel_models)
