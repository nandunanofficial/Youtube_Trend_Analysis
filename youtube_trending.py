import os
import requests
import pandas as pd
import nltk
from collections import Counter
from datetime import datetime
import re

# Download stopwords (needed only once)
nltk.download("stopwords")
from nltk.corpus import stopwords

# Set API Key and Region
API_KEY = os.getenv("YOUTUBE_API_KEY")  # Use environment variable
REGION = "IN"  # India
MAX_RESULTS = 50

def fetch_trending_videos():
    url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics&chart=mostPopular&regionCode={REGION}&maxResults={MAX_RESULTS}&key={API_KEY}"
    response = requests.get(url)
    
    if response.status_code != 200:
        print("Error fetching data:", response.json())
        return []

    data = response.json()
    videos = []

    for video in data.get("items", []):
        title = video["snippet"]["title"]
        description = video["snippet"]["description"]
        tags = video["snippet"].get("tags", [])

        # Combine title, description, and tags for keyword extraction
        text = f"{title} {description} {' '.join(tags)}"
        keywords = extract_keywords(text)

        videos.append({
            "Video ID": video["id"],
            "Title": title,
            "Description": description,
            "Tags": ", ".join(tags) if tags else "None",
            "Extracted Keywords": keywords,
            "Views": video["statistics"].get("viewCount", "0"),
            "Likes": video["statistics"].get("likeCount", "0"),
            "Comments": video["statistics"].get("commentCount", "0"),
            "Published Date": video["snippet"]["publishedAt"],
            "Trending Date": datetime.now().strftime("%Y-%m-%d")
        })

    return videos

def extract_keywords(text):
    # Clean and preprocess text
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    words = text.split()

    # Remove stopwords
    stop_words = set(stopwords.words("english"))
    filtered_words = [word for word in words if word not in stop_words]

    # Get top 10 keywords
    word_counts = Counter(filtered_words)
    top_keywords = [word for word, count in word_counts.most_common(10)]
    return ", ".join(top_keywords)

def save_to_csv(videos):
    filename = "youtube_trending_data.csv"
    
    # Convert to DataFrame
    df = pd.DataFrame(videos)

    # Save to CSV (append mode)
    df.to_csv(filename, mode="a", index=False, header=not os.path.exists(filename))
    print("Data collected and saved to", filename)

# Run script
videos = fetch_trending_videos()
if videos:
    save_to_csv(videos)
else:
    print("No data collected. Check API key or region settings.")
