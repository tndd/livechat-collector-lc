import os
import json

from dotenv import load_dotenv

import googleapiclient.discovery
import googleapiclient.errors

NEXT_PAGE_TOKEN_IS_EMPTY = 'empty_token'
SEARCH_LIST_DOWNLOAD_IS_COMPLETED = 'search_list_is_downloaded'

SAVE_DIR_PATH = '.youtube_data_api/search'

load_dotenv('.env')
os.makedirs(SAVE_DIR_PATH, exist_ok=True)


def is_exist_youtube_data_api_search(channel_id):
    return os.path.exists(f"{SAVE_DIR_PATH}/{channel_id}.json")


def get_videos_search_list_from_channel_id_part(channnel_id, next_page_token=None):
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

    return response.get('nextPageToken', NEXT_PAGE_TOKEN_IS_EMPTY), response['items']


def get_videos_search_list_from_channel_id(channel_id):
    if is_exist_youtube_data_api_search(channel_id):
        print(f"[SKIP]: SEARCH_LIST \"{channel_id}\" have already been downloaded.")
        return SEARCH_LIST_DOWNLOAD_IS_COMPLETED

    next_page_token = None
    videos_items = []
    while next_page_token != NEXT_PAGE_TOKEN_IS_EMPTY:
        next_page_token, video_items = get_videos_search_list_from_channel_id_part(channel_id, next_page_token)
        videos_items.extend(video_items)
    print(f"[Downloaded]: SEARCH_LIST \"{channel_id}\"")
    return videos_items


def main():
    channel_id = 'UCvaTdHTWBGv3MKj3KVqJVCw'
    for c_id in [channel_id]:
        videos_items = get_videos_search_list_from_channel_id(c_id)

        if videos_items == SEARCH_LIST_DOWNLOAD_IS_COMPLETED:
            continue

        with open(f"{SAVE_DIR_PATH}/{channel_id}.json", 'w') as f:
            json.dump(videos_items, f, ensure_ascii=False, indent=4)
        print(f"[STORED]: SEARCH_LIST \"{c_id}\"")


if __name__ == "__main__":
    main()
