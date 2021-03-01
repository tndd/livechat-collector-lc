from dataclasses import dataclass


@dataclass
class ChannelData:
    id: str
    code: str
    name: str

    def to_channel_table_row(self) -> tuple:
        return self.id, self.code, self.name
