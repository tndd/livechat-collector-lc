import requests
import re
import json
import os

from bs4 import BeautifulSoup


SAVE_DIR_PATH_Y_INITIAL_DATA = 'data/y_initial_data'
os.makedirs(SAVE_DIR_PATH_Y_INITIAL_DATA, exist_ok=True)


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


if __name__ == "__main__":
    video_id = 'AuOOuPTKC48'
    a = get_y_initial_data_from_video_id(video_id)
    store_y_initial_data(video_id, a)
