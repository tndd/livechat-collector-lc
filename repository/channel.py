import json

from typing import List

from service.client.channel_db_client import ChannelDBClient
from service.client.table.channel_data import ChannelData


class ChannelRepository:
    @classmethod
    def read_channels_obj_from_file(cls, path) -> dict:
        with open(path, 'r') as f:
            channels_obj = json.load(f)
        return channels_obj

    @classmethod
    def load_channel_models_into_db_from_file(cls) -> None:
        channels_obj = cls.read_channels_obj_from_file('./channel.json')
        channels_data = []
        for code, data in channels_obj.items():
            channels_data.append(
                ChannelData(
                    id=data['id'],
                    code=code,
                    name=data['name']
                )
            )
        ChannelDBClient.insert_channels_data_into_channel_table(channels_data)

    @classmethod
    def get_channels_data(cls) -> List[ChannelData]:
        channels_data = ChannelDBClient.select_channels_data()
        return channels_data

    @classmethod
    def get_channel_ids(cls) -> List[str]:
        channel_models = cls.get_channels_data()
        channel_ids = []
        for channel_model in channel_models:
            channel_ids.append(channel_model.id)
        return channel_ids
