import requests
import csv
import datetime
import base64

# YouTube API Key
API_KEY = os.getenv("API_YOUTUBE")

# List of YouTube Channel IDs (15 channels)
CHANNEL_IDS = [
    "UC_x5XG1OV2P6uZZ5FSM9Ttw",  # Example: Google Developers
    "UC-9-kyTW8ZkZNDHQJ6FgpwQ",  # Example: Music Channel
    "UC29ju8bIPH5as8OGnQzwJyA",  # Example: Traversy Media
    "UCSJbGtTlrDami-tDGPUV9-w",  # Example: NASA
    "UC4a-Gbdw7vOaccHmFo40b9g",
    "UCJbPGzawDH1njbqV-D5HqKw",
    "UCMUnInmOkrWN4gof9KlhNmQ",
    "UCW5YeuERMmlnqo4oq8vwUpg",
    "UCI8jB8K_UMBYVBDK6TkoqJw",
    "UC8butISFwT-Wl7EV0hUK0BQ",
    "UCsBjURrPoezykLs9EqgamOA",
    "UCYbK_tjZ2OrIZFBvU6CCMiA",
    "UC64oAui-2SgKpSlT-pjBX_g",
    "UCX6b17PVsYBQ0ip5gyeme-Q",
    "UCtinbF-Q-fVthA0qrFQTgXQ"
]

# GitHub Credentials
GITHUB_TOKEN = "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"
REPO_OWNER = "nandunanofficial"
REPO_NAME = "Youtube_Trend_Analysis"
FILE_PATH = "youtube_trends.csv"

# Function to fetch channel statistics
def get_channel_stats(channel_ids):
    stats_list = []
    for channel_id in channel_ids:
        url = f"https://www.googleapis.com/youtube/v3/channels?part=statistics&id={channel_id}&key={API_KEY}"
        response = requests.get(url)
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

# Function to get the latest file content & SHA
def get_file_sha():
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        content = response.json()
        return content.get("sha"), base64.b64decode(content["content"]).decode("utf-8")
    return None, None

# Function to update CSV file on GitHub
def update_github_file(data):
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    # Fetch existing content and SHA
    sha, existing_content = get_file_sha()
    csv_data = "Timestamp,Channel_ID,Subscribers,Views,Videos\n"
    
    if existing_content:
        csv_data += existing_content.split("\n", 1)[1]  # Keep header, append new data

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
        print("Data updated successfully on GitHub!")
    else:
        print("Error updating GitHub:", response.json())

# Fetch YouTube Data
channel_data = get_channel_stats(CHANNEL_IDS)
update_github_file(channel_data)
