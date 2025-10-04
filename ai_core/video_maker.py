import os
import requests
import time
import json
from dotenv import load_dotenv

load_dotenv()
SHOTSTACK_KEY = os.getenv("SHOTSTACK_API_KEY")
SHOTSTACK_STAGE = os.getenv("SHOTSTACK_STAGE", "stage") # Default to stage

def make_video_from_script(script_text):
    """Creates an animated video using the Shotstack API and returns the video URL."""
    if not SHOTSTACK_KEY:
        print("SHOTSTACK_API_KEY not found.")
        return None

    scenes = [s.strip() for s in script_text.split('.') if s.strip()]
    if not scenes:
        print("Script is empty or could not be split into sentences.")
        return None

    timeline_clips = []
    start_time = 0
    for sentence in scenes:
        duration = max(3.0, len(sentence.split()) / 3.0)
        video_clip = {
            "asset": {"type": "stock", "provider": "pexels", "search": sentence},
            "start": start_time,
            "length": duration
        }
        title_clip = {
            "asset": {"type": "title", "text": sentence, "style": "subtitle", "color": "#ffffff", "background": "#00000066"},
            "start": start_time,
            "length": duration
        }
        timeline_clips.extend([video_clip, title_clip])
        start_time += duration

    edit = {
        "timeline": {
            "background": "#000000",
            "tracks": [{"clips": timeline_clips}],
            "soundtrack": {"effect": "fadeInFadeOut", "src": script_text, "provider": "shotstack", "voice": "linda"}
        },
        "output": {"format": "mp4", "resolution": "sd"}
    }

    render_url = f"https://api.shotstack.io/{SHOTSTACK_STAGE}/render"
    headers = {
        "Content-Type": "application/json",
        "x-api-key": SHOTSTACK_KEY
    }

    # Step 1: Submit the job with a POST request
    try:
        response = requests.post(render_url, data=json.dumps(edit))
        response.raise_for_status()
        render_id = response.json()["response"]["id"]
        print(f"Successfully submitted job. Render ID: {render_id}")
    except Exception as e:
        print(f"Failed to submit render job to Shotstack: {e}")
        return None

    # Step 2: Check the status with a GET request to the correct URL, including the render_id
    status_url = f"{render_url}/{render_id}"
    while True:
        try:
            time.sleep(10)
            status_response = requests.get(status_url, headers=headers)
            status_response.raise_for_status()
            status = status_response.json()["response"]["status"]
            
            print(f"Current render status: {status}...")

            if status == "done":
                video_url = status_response.json()["response"]["url"]
                print(f"Video created successfully! URL: {video_url}")
                return video_url
            elif status == "failed":
                print(f"Shotstack render failed. Reason: {status_response.json()['response'].get('error')}")
                return None
        except Exception as e:
            print(f"Failed while checking render status: {e}")
            return None