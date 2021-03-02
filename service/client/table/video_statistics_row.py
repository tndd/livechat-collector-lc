from dataclasses import dataclass


@dataclass
class VideoStatisticsRow:
    video_id: str
    view_count: int
    like_count: int
    dislike_count: int

    def to_query_param(self) -> tuple:
        return (
            self.video_id,
            self.view_count,
            self.like_count,
            self.dislike_count
        )
