from dataclasses import dataclass
from typing import List


@dataclass
class VideoCollaboratedChannelIdRow:
    video_id: str
    collaborated_channel_id: str

    def to_query_param(self) -> tuple:
        return (
            self.video_id,
            self.collaborated_channel_id
        )
