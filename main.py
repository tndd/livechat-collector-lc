from repository.y_initial_data import YInitialDataRepository
from repository.video import VideoRepository

video_id = 'VZXmkSzfmCQ'
y_initial_data = YInitialDataRepository.load_y_initial_data_from_video_id(video_id)
a = VideoRepository.extract_collaborated_ids_from_y_initial_data(y_initial_data)
print(a)
