import os, requests, random
import xml.etree.ElementTree as ET
import google.generativeai as genai
from PIL import Image, ImageDraw

# Load Secrets
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
IG_USER_ID = os.getenv("IG_USER_ID")
ACCESS_TOKEN = os.getenv("META_ACCESS_TOKEN")
BASE_URL = os.getenv("BASE_URL")

def get_tech_news():
    rss = "https://news.google.com/rss/search?q=latest+tech+news&hl=en-IN"
    root = ET.fromstring(requests.get(rss).content)
    item = root.find('.//item')
    return item.find('title').text

def create_image(text):
    # Create 1080x1080 image
    img = Image.new('RGB', (1080, 1080), color=(15, 15, 15))
    d = ImageDraw.Draw(img)
    # Simple text placement (Center)
    d.text((540, 540), text[:60] + "...", fill=(255, 255, 255), anchor="mm")
    img.save("post.jpg")

def publish_to_ig(caption):
    image_url = f"{BASE_URL}/post.jpg"
    # Step 1: Upload to Meta
    post_url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media"
    payload = {'image_url': image_url, 'caption': caption, 'access_token': ACCESS_TOKEN}
    r = requests.post(post_url, data=payload).json()
    
    if 'id' in r:
        # Step 2: Publish the upload
        publish_url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media_publish"
        requests.post(publish_url, data={'creation_id': r['id'], 'access_token': ACCESS_TOKEN})
        print("Done! Check Instagram.")

if __name__ == "__main__":
    news = get_tech_news()
    create_image(news)
    # Give GitHub Pages a few seconds to update the file
    publish_to_ig(f"Tech Update: {news} #tech #ai")