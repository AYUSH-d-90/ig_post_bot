import os
import time
import requests
import textwrap
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont

# 1. --- CONFIGURATION & BRAIN ---
IG_USER_ID = os.getenv('IG_USER_ID')
META_ACCESS_TOKEN = os.getenv('META_ACCESS_TOKEN')
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

# We force Gemini to give us two distinct parts
prompt = "Write a viral tech news headline (max 10 words) and a 3-sentence business caption. Format exactly as: Headline | Caption"

try:
    response = model.generate_content(prompt)
    full_text = response.text.strip()
    # Splitting the AI response into the Image part and the IG part
    headline, caption = full_text.split('|')
except Exception as e:
    print(f"AI Error: {e}. Using backup.")
    headline = "AI Infrastructure Scaling Fast"
    caption = "Global systems are evolving to handle massive data loads. Today's tech is the foundation for tomorrow's finance."

# 2. --- THE FACTORY (Image Generation) ---
# Create a 1080x1080 (IG Square) Canvas
img = Image.new('RGB', (1080, 1080), color=(15, 15, 15)) 
d = ImageDraw.Draw(img)

# FONT SETTINGS: Small enough to fit, bold enough to read
font_size = 60 
try:
    # Standard Ubuntu path for GitHub Actions
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
except:
    font = ImageFont.load_default()

# WRAPPING: This stops the "Big Ass" text. It forces a new line every 20 characters.
wrapped_text = textwrap.fill(headline.strip(), width=20)

# CENTERING CALCULATION
bbox = d.multiline_textbbox((0, 0), wrapped_text, font=font, align="center")
w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]
# Draws the text exactly in the middle of the 1080px box
d.multiline_text(((1080-w)/2, (1080-h)/2), wrapped_text, font=font, fill=(255, 255, 255), align="center")

img.save("post.jpg")
print("✅ Image 'post.jpg' generated and saved.")

# 3. --- THE DELIVERY (Instagram Posting) ---
# THE CACHE BUSTER (?v=): This is the ONLY way to fix the "Same Image" error.
timestamp = int(time.time())
image_url = f"https://ayush-d-90.github.io/ig_post_bot/post.jpg?v={timestamp}"

# Combine headline and caption for the IG post
full_ig_caption = f"{headline.strip()}\n\n{caption.strip()}\n\n#TechNews #AI #Automation"

# Step A: Create Media Container
container_url = f"https://graph.facebook.com/v22.0/{IG_USER_ID}/media"
r1 = requests.post(container_url, data={
    'image_url': image_url, 
    'caption': full_ig_caption, 
    'access_token': META_ACCESS_TOKEN
})
res1 = r1.json()

if "id" in res1:
    creation_id = res1['id']
    print(f"✅ Container Created! ID: {creation_id}. Waiting for sync...")
    
    # Step B: The "Retry Loop" (Wait for Meta to process)
    publish_url = f"https://graph.facebook.com/v22.0/{IG_USER_ID}/media_publish"
    for i in range(3):
        time.sleep(45) # Give it 45 seconds per try
        r2 = requests.post(publish_url, data={'creation_id': creation_id, 'access_token': META_ACCESS_TOKEN})
        if "id" in r2.json():
            print(f"🚀 SUCCESS! Post is live. ID: {r2.json()['id']}")
            break
        else:
            print(f"Attempt {i+1}: Not ready yet...")
else:
    print(f"❌ Meta Error: {res1}")
