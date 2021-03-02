from dataclasses import dataclass


@dataclass
class ChannelRow:
    id: str
    code: str
    name: str

    def to_query_param(self) -> tuple:
        return self.id, self.code, self.name
