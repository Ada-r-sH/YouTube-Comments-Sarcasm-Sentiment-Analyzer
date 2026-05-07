import re
import html
import streamlit as st
from googleapiclient.discovery import build

API_KEY = st.secrets["YOUTUBE_API_KEY"]

def extract_video_id(url):
    regex = r"(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^\"&?\/\s]{11})"
    match = re.search(regex, url)
    return match.group(1) if match else None

def get_video_details(video_id):
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    request = youtube.videos().list(part="snippet,statistics", id=video_id)
    try:
        response = request.execute()
        if not response.get('items'):
            return None

        item = response['items'][0]
        return {
            "title": item['snippet']['title'],
            "channel": item['snippet']['channelTitle'],
            "thumbnail": item['snippet']['thumbnails']['high']['url'],
            "views": int(item['statistics'].get('viewCount', 0)),
            "likes": int(item['statistics'].get('likeCount', 0)),
            "comments": int(item['statistics'].get('commentCount', 0))
        }
    except Exception as e:
        st.error(f"API Error fetching video details: {e}")
        return None

def get_youtube_comments(video_id, max_comments=500):
    youtube = build('youtube', 'v3', developerKey=API_KEY)
    comments = []
    next_page_token = None

    while len(comments) < max_comments:
        try:
            request = youtube.commentThreads().list(
                part="snippet", videoId=video_id, maxResults=100,
                order="relevance", pageToken=next_page_token
            )
            response = request.execute()
        except Exception as e:
            st.error(f"YouTube API Error: {e}")
            break

        for item in response.get('items', []):
            snippet = item['snippet']['topLevelComment']['snippet']
            raw_text = snippet['textDisplay']
            clean_text = re.sub(r'<.*?>', ' ', raw_text)

            if len(clean_text.split()) < 5: continue

            comments.append({
                "text": html.unescape(clean_text),
                "likes": int(snippet.get('likeCount', 0))
            })
            if len(comments) >= max_comments: break

        next_page_token = response.get('nextPageToken')
        if not next_page_token: break

    return comments