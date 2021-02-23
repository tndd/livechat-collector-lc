import requests
import re
import json
import os

from bs4 import BeautifulSoup

from youtube_data_api import get_video_ids_from_channel_id


SAVE_DIR_PATH_Y_INITIAL_DATA = 'data/y_initial_data'
os.makedirs(SAVE_DIR_PATH_Y_INITIAL_DATA, exist_ok=True)


def is_exist_y_initial_data(video_id):
    return os.path.exists(f"{SAVE_DIR_PATH_Y_INITIAL_DATA}/{video_id}.json")


def clear_y_initial_data(video_id):
    if is_exist_y_initial_data(video_id):
        os.remove(f"{SAVE_DIR_PATH_Y_INITIAL_DATA}/{video_id}.json")


def get_y_initial_data_from_video_id(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'lxml')
    for element in soup.find_all('script'):
        content = str(element.string)
        if re.match(r'^(var ytInitialData = )', content):
            y_initial_data = content[len('var ytInitialData = '):-len(';')]
            return json.loads(y_initial_data)
    return None


def store_y_initial_data(video_id, y_initial_data):
    with open(f"{SAVE_DIR_PATH_Y_INITIAL_DATA}/{video_id}.json", 'w') as f:
        json.dump(y_initial_data, f, ensure_ascii=False, indent=4)
    print(f"[STORED]: Y_INITIAL_DATA \"{video_id}\"")


def download_y_initial_datas_from_channel_id(channel_id):
    video_ids = get_video_ids_from_channel_id(channel_id)
    for video_id in video_ids:
        if is_exist_y_initial_data(video_id):
            print(f"[SKIP]: Y_INITIAL_DATA \"{video_id}\" have already been downloaded.")
            continue
        try:
            y_initial_data = get_y_initial_data_from_video_id(video_id)
            store_y_initial_data(video_id, y_initial_data)
        except Exception as e:
            clear_y_initial_data(video_id)
            print(f"[ERROR]: Download Y_INITIAL_DATA \"{video_id}\" is missed.")
    print(f"[Completed]: Y_INITIAL_DATAS of \"{channel_id}\"")


def extract_video_data_from_y_initial_data(y_initial_data):
    # collaborated_ids
    # time_length
    # view_count
    # like_count
    # dislike_count
    pass


if __name__ == "__main__":
    channel_id = 'UCvaTdHTWBGv3MKj3KVqJVCw'
    download_y_initial_datas_from_channel_id(channel_id)
