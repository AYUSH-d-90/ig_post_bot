import os
import requests
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont

# 1. THE BRAIN (Gemini 1.5 Flash)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
# Using 'models/' prefix ensures the 404 error stays away
model = genai.GenerativeModel('models/gemini-1.5-flash')

try:
    prompt = "Write one short, exciting tech news headline for today in 10 words. No emojis."
    ai_response = model.generate_content(prompt)
    news_text = ai_response.text.strip()
except Exception as e:
    news_text = "Tech is moving fast today! Stay tuned." # Safety fallback

# 2. THE VISUAL (Big Text Logic)
img = Image.new('RGB', (1080, 1080), color=(15, 15, 15))
d = ImageDraw.Draw(img)
try:
    # Size 95: This makes the text bold and readable on mobile
    fnt = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 95)
except:
    fnt = ImageFont.load_default(size=85) # Fallback if system font moves

d.text((540, 540), news_text, fill=(255, 255, 255), anchor="mm", font=fnt)
img.save("post.jpg")

# 3. THE DELIVERY (Instagram API v22.0)
IG_USER_ID = os.getenv('IG_USER_ID')
META_ACCESS_TOKEN = os.getenv('META_ACCESS_TOKEN') # Your new May 2026 token

container_url = f"https://graph.facebook.com/v22.0/{IG_USER_ID}/media"
publish_url = f"https://graph.facebook.com/v22.0/{IG_USER_ID}/media_publish"
image_url = "https://ayush-d-90.github.io/ig_post_bot/post.jpg"

# STEP A: Tell Meta where the image is
payload = {'image_url': image_url, 'caption': news_text, 'access_token': META_ACCESS_TOKEN}
r1 = requests.post(container_url, data=payload)
res1 = r1.json()
import time # Make sure this is at the very top of your file!

# ... (Keep your Step A: Upload code the same)

if "id" in res1:
    creation_id = res1['id']
    print(f"Upload Success! Container ID: {creation_id}. Waiting for Meta to process...")
    
    # THE RETRY LOOP: Try 3 times, waiting 30 seconds between each
    for attempt in range(3):
        time.sleep(30) # Give Meta 30 seconds to "digest" the image
        
        publish_payload = {
            'creation_id': creation_id,
            'access_token': META_ACCESS_TOKEN
        }
        
        r2 = requests.post(publish_url, data=publish_payload)
        res2 = r2.json()
        
        if "id" in res2:
            print(f"FINAL SUCCESS! Post ID: {res2['id']}")
            break # Exit the loop because we succeeded!
        else:
            print(f"Attempt {attempt + 1} failed: {res2.get('error', {}).get('message')}")
            if attempt == 2: # If it's the last attempt
                print("Could not publish after 3 tries.")
                exit(1)
else:
    print(f"FAILED AT UPLOAD: {res1.get('error', {}).get('message')}")
    exit(1)
