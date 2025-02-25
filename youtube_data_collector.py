import os
import csv
import time
from googleapiclient.discovery import build
from datetime import datetime

# Fetch API Key from GitHub Secrets
API_KEY = os.getenv("API_YOUTUBE")

# Build YouTube API client
youtube = build("youtube", "v3", developerKey=API_KEY)

# Define CSV file path
CSV_FILE = "youtube_trending_data.csv"

# Function to fetch trending videos
def get_trending_videos():
    request = youtube.videos().list(
        part="snippet,statistics",
        chart="mostPopular",
        regionCode="IN",  # Change to "US" or other country if needed
        maxResults=10
    )
    response = request.execute()

    video_data = []
    for video in response.get("items", []):
        video_id = video["id"]
        title = video["snippet"]["title"]
        channel_id = video["snippet"]["channelId"]
        channel_title = video["snippet"]["channelTitle"]
        views = video["statistics"].get("viewCount", "0")
        likes = video["statistics"].get("likeCount", "0")
        comments = video["statistics"].get("commentCount", "0")
        
        # Fetch channel details
        channel_info = youtube.channels().list(
            part="statistics",
            id=channel_id
        ).execute()

        if channel_info["items"]:
            subs = channel_info["items"][0]["statistics"].get("subscriberCount", "0")
            total_videos = channel_info["items"][0]["statistics"].get("videoCount", "0")
            total_views = channel_info["items"][0]["statistics"].get("viewCount", "0")
        else:
            subs, total_videos, total_views = "0", "0", "0"

        video_data.append([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"), title, channel_title, 
            views, likes, comments, subs, total_videos, total_views, f"https://www.youtube.com/watch?v={video_id}"
        ])
    
    return video_data

# Function to save data to CSV
def save_to_csv(data):
    file_exists = os.path.isfile(CSV_FILE)
    with open(CSV_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(["Timestamp", "Title", "Channel", "Views", "Likes", "Comments", 
                             "Subscribers", "Total Videos", "Total Channel Views", "Video URL"])
        writer.writerows(data)

# Fetch and store trending videos
trending_videos = get_trending_videos()
save_to_csv(trending_videos)

print("✅ YouTube trending data updated successfully.")
