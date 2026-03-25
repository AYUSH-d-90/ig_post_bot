import os
import time
import requests
import textwrap
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont

# 1. --- CONFIGURATION ---
IG_USER_ID = os.getenv('IG_USER_ID')
META_ACCESS_TOKEN = os.getenv('META_ACCESS_TOKEN')
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. --- AI CONTENT GENERATION ---
# We ask for a "Headline | Caption" format to separate the image text from the IG description.
prompt = "Write a viral tech news headline (max 10 words) and a detailed 3-sentence business-focused caption. Format: Headline | Caption"

try:
    response = model.generate_content(prompt)
    full_text = response.text.strip()
    headline, caption = full_text.split('|')
except Exception as e:
    print(f"AI Error: {e}")
    headline = "Tech Innovation Scales Globally"
    caption = "Today's developments in AI and infrastructure are reshaping how global finance firms handle data at scale. Understanding these shifts is key for future systems."

# 3. --- VISUAL ARCHITECTURE (Smaller Font + Wrapping) ---
img = Image.new('RGB', (1080, 1080), color=(15, 15, 15)) # Dark Professional Background
d = ImageDraw.Draw(img)

# Decreased font size to 65 for a perfect fit
font_size = 65 
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)

# Wrapping text so it doesn't bleed off the 1080px box
lines = textwrap.wrap(headline.strip(), width=22) 
y_text = 540 - (len(lines) * font_size / 2) # Vertical Centering

for line in lines:
    bbox = d.textbbox((0, 0), line, font=font)
    w = bbox[2] - bbox[0]
    d.text(((1080 - w) / 2, y_text), line, font=font, fill=(255, 255, 255))
    y_text += font_size + 15

img.save("post.jpg")
print("✅ Image generated with wrapped text.")

# 4. --- INSTAGRAM DELIVERY (The Cache-Buster) ---
# ?v=timestamp forces Instagram to ignore yesterday's "Ghost" image
timestamp = int(time.time())
image_url = f"https://ayush-d-90.github.io/ig_post_bot/post.jpg?v={timestamp}"
full_caption = f"{headline.strip()}\n.\n.\n{caption.strip()}\n.\n#Tech #B2B #AI #Architecture"

# Step A: Create Container
container_url = f"https://graph.facebook.com/v22.0/{IG_USER_ID}/media"
r1 = requests.post(container_url, data={'image_url': image_url, 'caption': full_caption, 'access_token': META_ACCESS_TOKEN})
res1 = r1.json()

if "id" in res1:
    creation_id = res1['id']
    print(f"✅ Container Created: {creation_id}. Waiting for Meta sync...")
    
    # Step B: Wait and Publish (The "On-Time" Retry Loop)
    publish_url = f"https://graph.facebook.com/v22.0/{IG_USER_ID}/media_publish"
    for i in range(3):
        time.sleep(45) # Give Meta 45 seconds to 'digest' the image
        r2 = requests.post(publish_url, data={'creation_id': creation_id, 'access_token': META_ACCESS_TOKEN})
        if "id" in r2.json():
            print(f"🚀 POST IS LIVE! ID: {r2.json()['id']}")
            break
        else:
            print(f"Attempt {i+1} failed, retrying...")
else:
    print(f"❌ Meta API Error: {res1}")
