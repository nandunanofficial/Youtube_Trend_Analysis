import os
import csv
import time
from googleapiclient.discovery import build

# ✅ Get API Key from GitHub Secrets
API_KEY = os.getenv("YOUTUBE_API_KEY")

if not API_KEY:
    raise ValueError("❌ ERROR: YOUTUBE_API_KEY is missing! Add it to GitHub Secrets.")

# ✅ Initialize YouTube API
youtube = build("youtube", "v3", developerKey=API_KEY)

# ✅ CSV File Name (Stored in GitHub)
CSV_FILE = "youtube_trending.csv"

# ✅ Function to Fetch Trending Videos and Channel Data
def fetch_trending_videos():
    try:
        # ✅ Get Trending Videos (Top 10)
        request = youtube.videos().list(
            part="snippet,statistics",
            chart="mostPopular",
            maxResults=10,
            regionCode="IN"  # Change region if needed
        )
        response = request.execute()

        # ✅ Process Video Data
        trending_data = []
        for video in response['items']:
            video_id = video['id']
            title = video['snippet']['title']
            channel_id = video['snippet']['channelId']
            channel_name = video['snippet']['channelTitle']
            view_count = video['statistics'].get('viewCount', 'N/A')
            like_count = video['statistics'].get('likeCount', 'N/A')

            # ✅ Get Channel Details
            channel_request = youtube.channels().list(
                part="statistics",
                id=channel_id
            )
            channel_response = channel_request.execute()
            if channel_response["items"]:
                subscribers = channel_response["items"][0]["statistics"].get("subscriberCount", "N/A")
                total_videos = channel_response["items"][0]["statistics"].get("videoCount", "N/A")
            else:
                subscribers = "N/A"
                total_videos = "N/A"

            # ✅ Append Data
            trending_data.append([video_id, title, channel_name, subscribers, total_videos, view_count, like_count])

        return trending_data

    except Exception as e:
        print(f"❌ ERROR: {e}")
        return []

# ✅ Function to Write Data to CSV File
def save_to_csv(data):
    file_exists = os.path.isfile(CSV_FILE)

    with open(CSV_FILE, "a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        # ✅ Write Header If File is New
        if not file_exists:
            writer.writerow(["Video ID", "Title", "Channel Name", "Subscribers", "Total Videos", "Views", "Likes"])

        # ✅ Write Data
        writer.writerows(data)
        print(f"✅ Data Saved to {CSV_FILE}")

# ✅ Run Every Hour
while True:
    print("🚀 Fetching Trending YouTube Data...")
    trending_videos = fetch_trending_videos()

    if trending_videos:
        save_to_csv(trending_videos)

    print("⏳ Waiting 1 hour before next update...\n")
    time.sleep(3600)  # Wait for 1 hour
