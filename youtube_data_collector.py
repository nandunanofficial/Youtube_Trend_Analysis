import os
import pandas as pd
from datetime import datetime
from googleapiclient.discovery import build
import googleapiclient.errors

# Use GitHub Secrets for API Key
API_KEY = os.getenv("API_YOUTUBE")

# Initialize YouTube API
youtube = build("youtube", "v3", developerKey=API_KEY)
csv_filename = "youtube_trending_data.csv"

def fetch_trending_videos():
    try:
        request = youtube.videos().list(
            part="snippet,statistics",
            chart="mostPopular",
            maxResults=10,
            regionCode="IN"
        )
        response = request.execute()

        video_data = []
        for item in response["items"]:
            video_title = item["snippet"]["title"]
            video_views = item["statistics"].get("viewCount", "N/A")
            channel_id = item["snippet"]["channelId"]
            channel_name = item["snippet"]["channelTitle"]

            # Fetch channel details
            channel_request = youtube.channels().list(
                part="statistics",
                id=channel_id
            )
            channel_response = channel_request.execute()

            if channel_response["items"]:
                channel_stats = channel_response["items"][0]["statistics"]
                subscriber_count = channel_stats.get("subscriberCount", "N/A")
                total_videos = channel_stats.get("videoCount", "N/A")
                total_views = channel_stats.get("viewCount", "N/A")
            else:
                subscriber_count = total_videos = total_views = "N/A"

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            video_data.append([
                timestamp, video_title, channel_name, subscriber_count, total_videos, total_views, video_views
            ])

        df = pd.DataFrame(video_data, columns=[
            "Timestamp", "Video Title", "Channel Name", "Subscribers", "Total Videos", "Channel Views", "Video Views"
        ])

        df.to_csv(csv_filename, mode="a", header=not os.path.exists(csv_filename), index=False)
        print(f"✅ Data saved to {csv_filename} at {timestamp}")

    except googleapiclient.errors.HttpError as e:
        print(f"❌ API Request Failed: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    fetch_trending_videos()
