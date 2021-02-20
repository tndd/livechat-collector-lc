import json
import os

os.makedirs('channel-video-list', exist_ok=True)

### Mock data ###
fname = '.exam/output_youtube_data_api_search_list.json'
with open(fname, 'r') as f:
    data = json.loads(f.read())
#################

channel_data = {}
channel_data['channel_id'] = data['items'][0]['snippet']['channelId']
channel_data['channel_title'] = data['items'][0]['snippet']['channelTitle']

videos_data = {}
for d in data.get('items', []):
    videos_data[d['id']['videoId']] = {
        'title': d['snippet']['title'],
        'published_at': d['snippet']['publishedAt']
    }

channel_data.update(videos_data=videos_data)

with open(f"channel-video-list/{channel_data['channel_id']}.json", 'w') as f:
    f.write(json.dumps(channel_data, indent=4, ensure_ascii=False))
