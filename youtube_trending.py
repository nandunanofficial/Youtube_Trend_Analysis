import requests
import pandas as pd
import nltk
from collections import Counter
from datetime import datetime
import re

# Download stopwords (only needed once)
nltk.download('stopwords')

from nltk.corpus import stopwords

API_KEY = os.getenv("YOUTUBE_API_KEY")
REGION = "US"
MAX_RESULTS = 50

def fetch_trending_videos():
    url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&chart=mostPopular&regionCode={REGION}&maxResults={MAX_RESULTS}&key={API_KEY}"
    response = requests.get(url).json()

    videos = []
    for video in response.get("items", []):
        title = video["snippet"]["title"]
        description = video["snippet"]["description"]
        tags = video["snippet"].get("tags", [])
        
        # Combine text for keyword extraction
        text = title + " " + description + " " + " ".join(tags)
        
        videos.append({
            "Title": title,
            "Description": description,
            "Tags": tags,
            "Extracted_Keywords": extract_keywords(text),
            "Views": video["statistics"].get("viewCount", 0),
            "Likes": video["statistics"].get("likeCount", 0),
            "Comments": video["statistics"].get("commentCount", 0),
            "Trending_Date": datetime.now().strftime("%Y-%m-%d")
        })

    return videos

def extract_keywords(text):
    # Preprocess text
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    words = text.split()
    
    # Remove stopwords
    stop_words = set(stopwords.words("english"))
    filtered_words = [word for word in words if word not in stop_words]
    
    # Get top keywords
    word_counts = Counter(filtered_words)
    top_keywords = [word for word, count in word_counts.most_common(10)]  # Top 10 keywords
    return ", ".join(top_keywords)

# Fetch trending data and save to CSV
videos = fetch_trending_videos()
df = pd.DataFrame(videos)
df.to_csv("youtube_trending_data.csv", mode='a', index=False, header=False)

print("Data collected and saved.")
