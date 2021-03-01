from dataclasses import dataclass
from typing import List


@dataclass
class VideoCollaboratedChannelId:
    video_id: str
    collaborated_channel_id: str

    def to_row(self) -> tuple:
        return (
            self.video_id,
            self.collaborated_channel_id
        )
