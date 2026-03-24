import os
import requests
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont

# 1. SETUP AI (The Brain)
# Using the stable model name for Gemini 1.5 Flash
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

try:
    # 2. GENERATE NEWS
    prompt = "Write one short, exciting tech news headline for today in 10 words. No emojis in the headline."
    ai_response = model.generate_content(prompt)
    news_text = ai_response.text.strip()
    print(f"Generated News: {news_text}")
except Exception as e:
    print(f"AI Error: {e}")
    news_text = "Tech is evolving faster than ever today!" # Backup text

# 3. CREATE IMAGE (The Visual)
img = Image.new('RGB', (1080, 1080), color=(15, 15, 15)) # Sleek dark background
d = ImageDraw.Draw(img)

# --- 💡 BIGGER TEXT FIX ---
try:
    # Attempting to use a larger font size. 
    # 'load_default()' is very limited, so let's try a system font path (common on Ubuntu/GitHub)
    fnt = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 90)
    print("Using Custom Bold Font, Size 90")
except:
    # If the custom font fails, try a large default fallback (Size 80 is roughly max for default)
    fnt = ImageFont.load_default(size=80)
    print("Using Large Default Font Fallback")
# --- 💡 BIGGER TEXT FIX END ---

# Draw the text in the center
d.text((540, 540), news_text, fill=(255, 255, 255), anchor="mm", font=fnt)
img.save("post.jpg")
print("Image saved successfully.")

# 4. INSTAGRAM CREDENTIALS (FROM GITHUB SECRETS)
IG_USER_ID = os.getenv('IG_USER_ID')
META_ACCESS_TOKEN = os.getenv('META_ACCESS_TOKEN')

# 5. DEFINE URLS (Using latest Meta API v22.0)
container_url = f"https://graph.facebook.com/v22.0/{IG_USER_ID}/media"
publish_url = f"https://graph.facebook.com/v22.0/{IG_USER_ID}/media_publish"
# This link MUST be public and viewable in a browser
image_public_url = "https://ayush-d-90.github.io/ig_post_bot/post.jpg"

# 6. STEP A: UPLOAD THE CONTAINER
payload = {
    'image_url': image_public_url,
    'caption': f"{news_text} \n\n#TechNews #AI #TheTechBot #Automation",
    'access_token': META_ACCESS_TOKEN
}

print("Uploading to Instagram...")
r1 = requests.post(container_url, data=payload)
res1 = r1.json()

# 7. STEP B: PUBLISH THE POST
if "id" in res1:
    creation_id = res1['id']
    print(f"Upload Success! Container ID: {creation_id}")
    
    publish_payload = {
        'creation_id': creation_id,
        'access_token': META_ACCESS_TOKEN
    }
    
    r2 = requests.post(publish_url, data=publish_payload)
    print(f"FINAL STATUS: {r2.json()}")
else:
    print(f"FAILED AT UPLOAD: {res1.get('error', {}).get('message', 'Unknown Error')}")
    exit(1) # Forces GitHub to show a RED Error so you notice it
