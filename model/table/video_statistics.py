from dataclasses import dataclass


@dataclass
class VideoStatistics:
    video_id: str
    view_count: int
    like_count: int
    dislike_count: int

    def to_row(self) -> tuple:
        return (
            self.video_id,
            self.view_count,
            self.like_count,
            self.dislike_count
        )
