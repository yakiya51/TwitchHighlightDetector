import json
import matplotlib.pyplot as plt 
import os


def full_path(relative_path):
    base_path = os.path.abspath('.')
    return os.path.join(base_path, relative_path)


def to_mins(seconds):
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    return "%dh%02dm%02ds" % (hour, minutes, seconds)


if __name__ == '__main__':
    msg_to_check = []
    with open(full_path('config.txt'), 'r') as file:
        for i, line in enumerate(file.readlines()):
            if i == 0:
                INTERVAL = int(line[line.find('=')+1:].replace('\n', '').strip())
            elif i==1: 
                HYPE_CUTOFF = int(line[line.find('=')+1:].replace('\n', '').strip())
            elif i==2:
                temp = line[line.find('=')+1:].replace('\n', '').strip().lower()
                if temp =='true':
                    SHOW_GRAPH = True
                elif temp == 'false':
                    SHOW_GRAPH = False
                else:
                    raise Exception("Make sure the 'Show graph' part of the config is set to 'True' or 'False'.")
            elif line and i != 3:
                msg_to_check.append(line.replace('\n', ''))

    # JSON Chat data
    json_data = open(full_path('chat.json'), encoding='utf8')
    vod_data = json.load(json_data)

    # Meta Data of VOD
    video_meta = vod_data['video']
    video_id = vod_data['comments'][0]['content_id']
    start_time = int(video_meta['start'])
    end_time = int(video_meta['end'])

    # Time : Chat
    chat_data = {}

    # Set up time intervals
    for time in range(start_time, end_time + INTERVAL, INTERVAL):
        chat_data[time] = 0

    # Fill in chat_data
    current_key = 0
    time_keys = list(chat_data.keys())

    for comment in vod_data['comments']:
        msg = comment['message']['body'].lower()
        for expression in msg_to_check:
            if msg.find(expression) != -1:
                msg_time = comment['content_offset_seconds']
                while time_keys[current_key] < msg_time:
                    current_key += 1
                chat_data[time_keys[current_key]] += 1

    keys = list(time_keys)
    values = list(chat_data.values())

    # Print out vod time stamp links
    for time in chat_data:
        if chat_data[time] >= HYPE_CUTOFF:
            print(f"https://www.twitch.tv/videos/{video_id}?t={to_mins(time)}  | Hype Msgs: {chat_data[time]}")

    print(f'\nMOST HYPE MSGS IN ONE INTERVAL: {max(values)}')

    if SHOW_GRAPH:
        plt.figure(figsize=(13, 5))
        plt.plot(keys,values)
        plt.title('Twitch Chat Hype Tracker')
        plt.ylabel('Hype Msg Count')
        plt.xlabel('Time in VOD')
        plt.show()



