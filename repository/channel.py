import json

from dataclasses import dataclass
from typing import Dict, List


ChannelCode = str
ChannelId = str


@dataclass
class ChannelModel:
    id: ChannelId
    name: str


@dataclass
class ChannelRepository:
    channel_file_path = './channel.json'

    @classmethod
    def load_channels_data(cls) -> dict:
        with open(cls.channel_file_path, 'r') as f:
            channels_data = json.load(f)
        return channels_data

    @staticmethod
    def conversion_channel_data_to_model(channel_data: dict) -> ChannelModel:
        return ChannelModel(
            id = channel_data['id'],
            name = channel_data['name']
        )

    @classmethod
    def get_code_channel_models(cls) -> Dict[ChannelCode, ChannelModel]:
        channels_data = cls.load_channels_data()
        code_channel_models = {}
        for code, data in channels_data.items():
            code_channel_models[code] = cls.conversion_channel_data_to_model(data)
        return code_channel_models

    @classmethod
    def get_channel_ids(cls) -> List[ChannelId]:
        code_channel_models = cls.get_code_channel_models()
        channel_ids = []
        for channel_model in code_channel_models.values():
            channel_ids.append(channel_model.id)
        return channel_ids
