import os
import requests
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont

# 1. SETUP AI (The Brain)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. GENERATE NEWS
response = model.generate_content("Write one short, exciting tech news headline for today in 10 words.")
news_text = response.text.strip()
print(f"Generated News: {news_text}")

# 3. CREATE IMAGE (The Visual)
img = Image.new('RGB', (1080, 1080), color=(20, 20, 20)) # Dark background
d = ImageDraw.Draw(img)
# Note: Ensure you have a font file or use default
try:
    fnt = ImageFont.truetype("arial.ttf", 60)
except:
    fnt = ImageFont.load_default()

d.text((540, 540), news_text, fill=(255, 255, 255), anchor="mm")
img.save("post.jpg")
print("Image saved as post.jpg")

# 4. INSTAGRAM CREDENTIALS
IG_USER_ID = os.getenv('IG_USER_ID')
META_ACCESS_TOKEN = os.getenv('META_ACCESS_TOKEN')

# 5. DEFINE URLS
container_url = f"https://graph.facebook.com/v22.0/{IG_USER_ID}/media"
publish_url = f"https://graph.facebook.com/v22.0/{IG_USER_ID}/media_publish"
image_link = "https://ayush-d-90.github.io/ig_post_bot/post.jpg"

# 6. STEP A: UPLOAD TO META
payload = {
    'image_url': image_link,
    'caption': f"{news_text} #TechNews #AI",
    'access_token': META_ACCESS_TOKEN
}

print("Uploading to Instagram...")
ig_response = requests.post(container_url, data=payload)
result = ig_response.json()

# 7. STEP B: PUBLISH
if "id" in result:
    creation_id = result['id']
    publish_payload = {'creation_id': creation_id, 'access_token': META_ACCESS_TOKEN}
    final_post = requests.post(publish_url, data=publish_payload)
    print(f"SUCCESS! Post ID: {final_post.json()}")
else:
    print(f"META ERROR: {result.get('error', {}).get('message')}")
    exit(1)
