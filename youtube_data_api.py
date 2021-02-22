import os
import json

from dotenv import load_dotenv

import googleapiclient.discovery
import googleapiclient.errors


NEXT_PAGE_TOKEN_IS_EMPTY = 'empty_token'
SEARCH_LIST_DOWNLOAD_IS_COMPLETED = 'search_list_is_downloaded'

SAVE_DIR_PATH_SEARCH = 'data/youtube_data_api/search'
SAVE_DIR_PATH_VIDEOS = 'data/youtube_data_api/videos'

load_dotenv('.env')
os.makedirs(SAVE_DIR_PATH_SEARCH, exist_ok=True)
os.makedirs(SAVE_DIR_PATH_VIDEOS, exist_ok=True)


class NotExistSearchListDataError(Exception):
    pass


class NotExistVideosDataError(Exception):
    pass


class NotExistChannelsDataError(Exception):
    pass


def is_exist_youtube_data_api_search(channel_id):
    return os.path.exists(f"{SAVE_DIR_PATH_SEARCH}/{channel_id}.json")


def is_exist_youtube_data_api_video(video_id):
    return os.path.exists(f"{SAVE_DIR_PATH_VIDEOS}/{video_id}.json")


def clear_video_item(video_id):
    if is_exist_youtube_data_api_video(video_id):
        os.remove(f"{SAVE_DIR_PATH_VIDEOS}/{video_id}.json")


def load_youtube_data_api_search_list(channel_id):
    try:
        with open(f"{SAVE_DIR_PATH_SEARCH}/{channel_id}.json", 'r') as f:
            search_list = json.load(f)
    except FileNotFoundError as e:
        message = f"[ERROR] Channel id: \"{channel_id}\" search list data is not exist."
        raise NotExistSearchListDataError(message)
    except Exception as e:
        raise e
    return search_list


def load_youtube_data_api_videos_data(video_id):
    try:
        with open(f"{SAVE_DIR_PATH_VIDEOS}/{video_id}.json", 'r') as f:
            videos_data = json.load(f)
    except FileNotFoundError as e:
        message = f"[ERROR] Video id: \"{video_id}\" videos data is not exist."
        raise NotExistVideosDataError(message)
    except Exception as e:
        raise e
    return videos_data


def load_channels_data():
    try:
        with open('channel.json', 'r') as f:
            channels_data = json.load(f)
    except FileNotFoundError as e:
        message = '[ERROR] Channels data is not exist.'
        raise NotExistChannelsDataError(message)
    except Exception as e:
        raise e
    return channels_data


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
        pageToken=next_page_token
    )
    response = request.execute()

    return response.get('nextPageToken', NEXT_PAGE_TOKEN_IS_EMPTY), response['items']


def get_channel_search_list_from_channel_id(channel_id):
    if is_exist_youtube_data_api_search(channel_id):
        print(f"[SKIP]: SEARCH_LIST \"{channel_id}\" have already been downloaded.")
        return SEARCH_LIST_DOWNLOAD_IS_COMPLETED

    next_page_token = None
    search_list = []
    while next_page_token != NEXT_PAGE_TOKEN_IS_EMPTY:
        next_page_token, search_list_part = get_channel_search_list_from_channel_id_part(channel_id, next_page_token)
        search_list.extend(search_list_part)
    print(f"[Downloaded]: SEARCH_LIST \"{channel_id}\"")
    return search_list


def get_video_ids_from_channel_id(channel_id):
    search_list = load_youtube_data_api_search_list(channel_id)
    video_ids = []
    for item in search_list:
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


def store_channel_search_list(channel_id, search_list):
    with open(f"{SAVE_DIR_PATH_SEARCH}/{channel_id}.json", 'w') as f:
        json.dump(search_list, f, ensure_ascii=False, indent=4)
    print(f"[STORED]: SEARCH_LIST \"{channel_id}\"")


def store_video_item(video_id, video_item):
    with open(f"{SAVE_DIR_PATH_VIDEOS}/{video_id}.json", 'w') as f:
        json.dump(video_item, f, ensure_ascii=False, indent=4)
    print(f"[STORED]: VIDEO_ITEM \"{video_id}\"")


def download_channel_search_list():
    # get channel_list's video data and store.
    with open('channel.json', 'r') as f:
        channel_items = json.load(f)
    for talent_code, channel_data in channel_items.items():
        search_list = get_channel_search_list_from_channel_id(channel_data['id'])

        if search_list == SEARCH_LIST_DOWNLOAD_IS_COMPLETED:
            continue

        store_channel_search_list(channel_data['id'], search_list)


def download_video_items_from_channel_id(channel_id):
    video_ids = get_video_ids_from_channel_id(channel_id)
    for video_id in video_ids:
        if is_exist_youtube_data_api_video(video_id):
            print(f"[SKIP]: VIDEO_ITEM \"{video_id}\" have already been downloaded.")
            continue
        try:
            video_item = get_video_item_from_video_id(video_id)
            store_video_item(video_id, video_item)
        except Exception as e:
            clear_video_item(video_id)
            print(f"[ERROR]: Download VIDEO_ITEM \"{video_id}\" is missed.")
    print(f"[Completed]: VIDEO_ITEMS of \"{channel_id}\"")


def main():
    # download_channel_search_list()
    channel_id = 'UCvaTdHTWBGv3MKj3KVqJVCw'
    download_video_items_from_channel_id(channel_id)


if __name__ == "__main__":
    main()
