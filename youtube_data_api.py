import os
import json

from dotenv import load_dotenv

import googleapiclient.discovery
import googleapiclient.errors


NEXT_PAGE_TOKEN_IS_EMPTY = 'empty_token'
SEARCH_LIST_DOWNLOAD_IS_COMPLETED = 'search_list_is_downloaded'

SAVE_DIR_PATH_SEARCH = '.youtube_data_api/search'
SAVE_DIR_PATH_VIDEOS = '.youtube_data_api/videos'

load_dotenv('.env')
os.makedirs(SAVE_DIR_PATH_SEARCH, exist_ok=True)
os.makedirs(SAVE_DIR_PATH_VIDEOS, exist_ok=True)


class NotExistSearchListDataError(Exception):
    pass


def is_exist_youtube_data_api_search(channel_id):
    return os.path.exists(f"{SAVE_DIR_PATH_SEARCH}/{channel_id}.json")


def get_youtube_api_client():
    api_service_name = "youtube"
    api_version = "v3"
    api_key = os.environ.get("YOUTUBE_DATA_API_KEY")

    youtube_api_client = googleapiclient.discovery.build(
        api_service_name,
        api_version,
        developerKey=api_key
    )
    return youtube_api_client


def get_channel_search_list_from_channel_id_part(channnel_id, next_page_token=None):
    youtube_api_client = get_youtube_api_client()
    request = youtube_api_client.search().list(
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


def get_channel_search_list_from_channel_id(channel_id):
    if is_exist_youtube_data_api_search(channel_id):
        print(f"[SKIP]: SEARCH_LIST \"{channel_id}\" have already been downloaded.")
        return SEARCH_LIST_DOWNLOAD_IS_COMPLETED

    next_page_token = None
    channel_search_items = []
    while next_page_token != NEXT_PAGE_TOKEN_IS_EMPTY:
        next_page_token, item = get_channel_search_list_from_channel_id_part(channel_id, next_page_token)
        channel_search_items.extend(item)
    print(f"[Downloaded]: SEARCH_LIST \"{channel_id}\"")
    return channel_search_items


def store_channel_search_list(channel_id, channel_search_items):
    with open(f"{SAVE_DIR_PATH_SEARCH}/{channel_id}.json", 'w') as f:
        json.dump(channel_search_items, f, ensure_ascii=False, indent=4)
    print(f"[STORED]: SEARCH_LIST \"{channel_id}\"")


def task_channel_search_list():
    # download channel_list's video data and store.
    with open('channel.json', 'r') as f:
        channel_items = json.load(f)
    for talent_name, channel_id in channel_items.items():
        channel_search_items = get_channel_search_list_from_channel_id(channel_id)

        if channel_search_items == SEARCH_LIST_DOWNLOAD_IS_COMPLETED:
            continue

        store_channel_search_list(channel_id, channel_search_items)


def get_video_ids_from_channel_id(channel_id):
    try:
        with open(f"{SAVE_DIR_PATH_SEARCH}/{channel_id}.json", 'r') as f:
            search_list_items = json.load(f)
    except FileNotFoundError as e:
        message = f"[ERROR] Channel id: \"{channel_id}\" search list data is not exist."
        raise NotExistSearchListDataError(message)
    except Exception as e:
        raise e

    video_ids = []
    for item in search_list_items:
        video_ids.append(item['id']['videoId'])

    return video_ids


def get_video_item_from_video_id(video_id):
    youtube_api_client = get_youtube_api_client()
    request = youtube_api_client.videos().list(
        part="snippet,contentDetails,id,liveStreamingDetails,localizations,player,recordingDetails,statistics,status,topicDetails,recordingDetails",
        id=video_id
    )
    response = request.execute()
    return response


def main():
    # task_channel_search_list()
    a = get_video_item_from_video_id("ZK1GXnz-1Lw")
    with open('out.json', 'w') as f:
        json.dump(a, f, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    main()
