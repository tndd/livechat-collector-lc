from dataclasses import dataclass
from datetime import datetime


@dataclass
class VideoRow:
    id: str
    channel_id: str
    published_at: datetime
    title: str

    def to_query_param(self) -> tuple:
        return (
            self.id,
            self.channel_id,
            self.published_at.strftime('%Y-%m-%d %H:%M:%S'),
            self.title
        )
