import requests
import re
import json

from bs4 import BeautifulSoup


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


if __name__ == "__main__":
    video_id = 'AuOOuPTKC48'
    a = get_y_initial_data_from_video_id(video_id)
    print(a)
