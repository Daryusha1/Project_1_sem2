import os
import pandas as pd
import requests
from dotenv import load_dotenv
import time

load_dotenv()

api_key = os.getenv("API_KEY")
if not api_key:
    raise ValueError("API_KEY не найден! Проверь файл .env.")

# Список наших интервью
videos = {
    "sobchak_blinovskaya": "jSci-uMyUHo",  # Блиновская
    "sobchak_buzova": "9JD31-qgba4",        # Бузова
    "sobchak_morgenstern2": "NXeYwMPYdmM"   # Моргенштерн 2 интервью
}

# Функция для скачивания комментариев
def get_comments(video_id, api_key):
    comments = []
    url = f"https://www.googleapis.com/youtube/v3/commentThreads?part=snippet&videoId={video_id}&maxResults=100&key={api_key}"

    while url:
        response = requests.get(url)
        data = response.json()

        for item in data.get('items', []):
            comment = item['snippet']['topLevelComment']['snippet']
            comments.append({
                "author": comment.get("authorDisplayName"),
                "text": comment.get("textDisplay"),
                "publishedAt": comment.get("publishedAt"),
                "likes": comment.get("likeCount")
            })

        next_page_token = data.get('nextPageToken')
        if next_page_token:
            url = f"https://www.googleapis.com/youtube/v3/commentThreads?part=snippet&videoId={video_id}&maxResults=100&key={api_key}&pageToken={next_page_token}"
            time.sleep(1)
        else:
            url = None

    return pd.DataFrame(comments)

# Сбор данных по каждому видео
for name, video_id in videos.items():
    df = get_comments(video_id, api_key)
    output_path = f"../data/{name}_comments_raw.csv"
    df.to_csv(output_path, index=False)
