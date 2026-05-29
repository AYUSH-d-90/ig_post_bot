import os
import time
import requests
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont
import textwrap

IG_USER_ID = os.getenv("IG_USER_ID")
GENAI_API_KEY = os.getenv("GEMINI_API_KEY")
ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
BASE_URL = os.getenv("BASE_URL")

genai.configure(api_key=GENAI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

import random

def get_tech_news():
    try:
        # We use a unique separator '@@@' because Gemini is less likely to use it accidentally
        prompt = "Provide one trending tech news. Format: TITLE @@@ DESCRIPTION. Do not include any other text."
        response = model.generate_content(prompt)
        text = response.text
        
        # This is where your error was happening. Now we check the length first.
        if "@@@" in text:
            data = text.split("@@@")
            if len(data) >= 2:
                return data[0].strip(), data[1].strip()
        
        # FALLBACK: If Gemini messes up the format, this keeps the bot alive
        print("Format error from AI, using fallback parsing.")
        return "Tech Update", text.strip()[:100] 

    except Exception as e:
        print(f"Error calling Gemini: {e}")
        return "Tech News", "Check back later for more updates!"

def create_image(headline):
    img = Image.new('RGB', (1080, 1080), color=(15, 15, 15))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 65)
    except:
        font = ImageFont.load_default()

    lines = textwrap.wrap(headline, width=25)
    y_text = 400
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        draw.text(((1080 - w) / 2, y_text), line, font=font, fill=(255, 255, 255))
        y_text += 80

    filename = "latest_post.jpg" # Kept simple for the URL
    img.save(filename)
    return filename

def post_to_instagram(image_name, caption):
    # 1. Wait for GitHub CDN to refresh so Meta doesn't 404
    print("Waiting 15 seconds for GitHub to process the image...")
    time.sleep(15)

    # 2. Get environment variables
    ig_user_id = os.getenv('IG_USER_ID')
    access_token = os.getenv('META_ACCESS_TOKEN')
    repo = os.getenv('GITHUB_REPOSITORY') 
    
    # Cache buster to force Meta to grab the newest file
    timestamp = int(time.time())
    image_url = f"https://raw.githubusercontent.com/{repo}/main/{image_name}?v={timestamp}"
    
    print(f"Target Image URL: {image_url}")

    # 3. STEP 1: Create the Media Container
    container_url = f"https://graph.facebook.com/v19.0/{ig_user_id}/media"
    container_payload = {
        'image_url': image_url,
        'caption': caption,
        'access_token': access_token
    }
    
    print("Creating Meta container...")
    container_res = requests.post(container_url, data=container_payload).json()
    print(f"Container Response: {container_res}")
    
    # SAFETY: Stop the script if Meta didn't give us an ID
    if 'id' not in container_res:
        print("CRITICAL: Container creation failed. Stopping script to avoid 'None' error.")
        return
        
    container_id = container_res['id']

    # 4. Wait for Meta to finish processing the image internally
    print("Container created. Waiting 5 seconds before publishing...")
    time.sleep(5)

    # 5. STEP 2: Publish the Container to Feed
    publish_url = f"https://graph.facebook.com/v19.0/{ig_user_id}/media_publish"
    publish_payload = {
        'creation_id': container_id,
        'access_token': access_token
    }
    
    print("Publishing to Instagram...")
    publish_res = requests.post(publish_url, data=publish_payload).json()
    print(f"Publish Response: {publish_res}")

    if 'id' in publish_res:
        print("Success! Post is live on Instagram.")
    else:
        print("Failed to publish container.")
