from dataclasses import dataclass


@dataclass
class ChannelModel:
    id: str
    code: str
    name: str

    def to_channel_table_row(self) -> tuple:
        return self.id, self.code, self.name
