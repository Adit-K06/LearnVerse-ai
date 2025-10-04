import os
import requests
import time
from dotenv import load_dotenv

load_dotenv()
D_ID_KEY = os.getenv("D_ID_API_KEY")

def create_animated_clip(script_text):
    """Creates a video of a talking presenter using the D-ID API and returns the video URL."""
    if not D_ID_KEY:
        print("D_ID_API_KEY not found.")
        return None

    create_url = "https://api.d-id.com/animations"
    
    payload = {
        "script": {
            "type": "text",
            "input": script_text,
            "provider": {"type": "microsoft", "voice_id": "en-US-JennyNeural"}
        },
        "source_url": "https://create-images-results.d-id.com/DefaultPresenters/Naomi_f/image.jpeg", # Stock presenter
        "config": {"result_format": "mp4"}
    }
    
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Basic {D_ID_KEY}"
    }

    try:
        # POST request to start video generation
        response = requests.post(create_url, json=payload, headers=headers)
        response.raise_for_status()
        
        talk_id = response.json().get("id")
        if not talk_id:
            print("Failed to get talk ID from D-ID.")
            return None

        # Poll the API to check for video completion
        get_url = f"https://api.d-id.com/talks/{talk_id}"
        while True:
            time.sleep(5)
            get_response = requests.get(get_url, headers=headers)
            get_response.raise_for_status()
            
            result = get_response.json()
            status = result.get("status")

            if status == "done":
                video_url = result.get("result_url")
                print(f"Video created successfully! URL: {video_url}")
                return video_url
            elif status == "error":
                print(f"D-ID video generation failed: {result.get('error')}")
                return None

    except requests.exceptions.RequestException as e:
        print(f"An API error occurred: {e}")
        if e.response:
            print(f"Response Body: {e.response.text}")
        return None