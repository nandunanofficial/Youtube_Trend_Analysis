import os
import requests
import csv
import datetime
import base64

# Fetch API keys & tokens from GitHub Secrets
API_KEY = os.getenv("API_YOUTUBE")
GITHUB_TOKEN = os.getenv("GH_PAT")  # Use GitHub secret instead of hardcoding

# GitHub Repository Info
REPO_OWNER = "nandunanofficial"
REPO_NAME = "Youtube_Trend_Analysis"
FILE_PATH = "youtube_trends.csv"

# YouTube Channel IDs (15 channels)
CHANNEL_IDS = [
    "UC_x5XG1OV2P6uZZ5FSM9Ttw", "UC-9-kyTW8ZkZNDHQJ6FgpwQ",
    "UC29ju8bIPH5as8OGnQzwJyA", "UCSJbGtTlrDami-tDGPUV9-w",
    "UC4a-Gbdw7vOaccHmFo40b9g", "UCJbPGzawDH1njbqV-D5HqKw",
    "UCMUnInmOkrWN4gof9KlhNmQ", "UCW5YeuERMmlnqo4oq8vwUpg",
    "UCI8jB8K_UMBYVBDK6TkoqJw", "UC8butISFwT-Wl7EV0hUK0BQ",
    "UCsBjURrPoezykLs9EqgamOA", "UCYbK_tjZ2OrIZFBvU6CCMiA",
    "UC64oAui-2SgKpSlT-pjBX_g", "UCX6b17PVsYBQ0ip5gyeme-Q",
    "UCtinbF-Q-fVthA0qrFQTgXQ"
]

# Function to fetch channel statistics
def get_channel_stats(channel_ids):
    stats_list = []
    for channel_id in channel_ids:
        url = f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id={channel_id}&key={API_KEY}"
        response = requests.get(url)
        
        if response.status_code != 200:
            print(f"Failed to fetch data for {channel_id}: {response.json()}")
            continue  # Skip if error occurs
        
        data = response.json()
        if "items" in data:
            stats = data["items"][0]["statistics"]
            stats_list.append([
                str(datetime.datetime.now()),  # Timestamp
                channel_id,
                stats.get("subscriberCount", 0),
                stats.get("viewCount", 0),
                stats.get("videoCount", 0)
            ])
    
    return stats_list

# Function to get file SHA & existing content
def get_file_sha():
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        content = response.json()
        return content.get("sha"), base64.b64decode(content["content"]).decode("utf-8")
    elif response.status_code == 404:
        return None, None  # File doesn't exist, create a new one
    else:
        print(f"Error fetching file SHA: {response.json()}")
        return None, None

# Function to update CSV file on GitHub
def update_github_file(data):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"Bearer {GITHUB_TOKEN}"}
    
    # Fetch existing content & SHA
    sha, existing_content = get_file_sha()
    csv_data = "Timestamp,Channel_ID,Subscribers,Views,Videos\n"  # CSV Header

    if existing_content:
        csv_data += existing_content.split("\n", 1)[1]  # Keep previous data

    for row in data:
        csv_data += ",".join(map(str, row)) + "\n"

    # Upload new content
    payload = {
        "message": "Updated YouTube trends data",
        "content": base64.b64encode(csv_data.encode("utf-8")).decode("utf-8"),
        "sha": sha if sha else None
    }
    
    response = requests.put(url, headers=headers, json=payload)
    if response.status_code in [200, 201]:
        print("✅ Data updated successfully on GitHub!")
    else:
        print(f"❌ Error updating GitHub: {response.json()}")

# Fetch YouTube Data
if not API_KEY or not GITHUB_TOKEN:
    print("❌ API_KEY or GITHUB_TOKEN is missing. Check your GitHub Secrets.")
else:
    channel_data = get_channel_stats(CHANNEL_IDS)
    if channel_data:
        update_github_file(channel_data)
    else:
        print("⚠️ No data fetched from YouTube API.")
