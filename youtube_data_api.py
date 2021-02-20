import os
import json

from dotenv import load_dotenv

import googleapiclient.discovery
import googleapiclient.errors

EMPTY_TOKEN = 'empty_token'
SAVE_DIR_PATH = '.youtube_data_api/search'

load_dotenv('.env')
os.makedirs(SAVE_DIR_PATH, exist_ok=True)


def get_videos_search_list_part(channnel_id, next_page_token=None):
    api_service_name = "youtube"
    api_version = "v3"
    api_key = os.environ.get("YOUTUBE_DATA_API_KEY")

    youtube = googleapiclient.discovery.build(
        api_service_name,
        api_version,
        developerKey=api_key
    )
    request = youtube.search().list(
        part="snippet",
        channelId=channnel_id,
        eventType="completed",
        maxResults=50,
        order="date",
        type="video",
        pageToken = next_page_token
    )
    response = request.execute()

    return response.get('nextPageToken', EMPTY_TOKEN), response['items']


def get_videos_search_list_part(channel_id):
    next_page_token = None
    videos_items = []
    while next_page_token != EMPTY_TOKEN:
        print(next_page_token)
        next_page_token, video_items = get_videos_search_list_part(channel_id, next_page_token)
        videos_items.extend(video_items)
    return videos_items


def main():
    channel_id = 'UCvaTdHTWBGv3MKj3KVqJVCw'
    videos_items = get_videos_search_list_part(channel_id)

    with open(f"{SAVE_DIR_PATH}/{channel_id}.json", 'w') as f:
        json.dump(videos_items, f, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
