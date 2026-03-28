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
    # Adding a random "seed" word forces the AI to pick different topics
    topics = ["AI", "Hardware", "Robotics", "SpaceTech", "Cybersecurity", "Software"]
    chosen_topic = random.choice(topics)
    
    prompt = f"Give me one unique, recent news headline about {chosen_topic} and a 3-sentence caption. Format: Headline | Caption. Ensure it is different from common daily headlines."
    
    response = model.generate_content(prompt)
    data = response.text.split("|")
    return data[0].strip(), data[1].strip()

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

def post_to_instagram(image_filename, caption):
    # This combines your secret BASE_URL with the filename
    image_url = f"{BASE_URL}{image_filename}?v={int(time.time())}"
    print(f"DEBUG: Posting URL is {image_url}")

    post_url = f"https://graph.facebook.com/v22.0/{IG_USER_ID}/media"
    payload = {
        'image_url': image_url,
        'caption': caption,
        'access_token': ACCESS_TOKEN
    }
    
    r = requests.post(post_url, data=payload)
    result = r.json()
    
    if 'id' not in result:
        print(f"Container Error: {result}")
        return

    creation_id = result['id']
    publish_url = f"https://graph.facebook.com/v22.0/{IG_USER_ID}/media_publish"
    
    # Retry loop to wait for Meta to finish downloading
    for attempt in range(5):
        time.sleep(60)
        publish_res = requests.post(publish_url, data={
            'creation_id': creation_id,
            'access_token': ACCESS_TOKEN
        })
        if publish_res.status_code == 200:
            print("Post Successful!")
            return
        print(f"Attempt {attempt+1} failed, retrying...")

if __name__ == "__main__":
    title, desc = get_tech_news()
    img_file = create_image(title)
    # We save the caption to a file so the next step in the YAML can read it
    with open("caption.txt", "w") as f:
        f.write(f"{title}\n\n{desc}\n\n#tech #automation")
    # Actually call the post function
    post_to_instagram(img_file, f"{title}\n\n{desc}")
