import os
import requests
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont


genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

try:
    model = genai.GenerativeModel('gemini-1.5-flash')
    print("Trying Model Name: gemini-1.5-flash")
    prompt = "Write one short, exciting tech news headline for today in 10 words. No emojis."
    ai_response = model.generate_content(prompt)
    news_text = ai_response.text.strip()
except Exception:
    try:
        model = genai.GenerativeModel('models/gemini-1.5-flash')
        print("Trying Model Name: models/gemini-1.5-flash")
        ai_response = model.generate_content(prompt)
        news_text = ai_response.text.strip()
    except Exception as e:
        print(f"Final AI Error: {e}")
        news_text = "AI is changing the world in 2026!" 

try:
    prompt = "Write one short, exciting tech news headline for today in 10 words. No emojis."
    ai_response = model.generate_content(prompt)
    news_text = ai_response.text.strip()
except Exception as e:
    news_text = "Tech is moving fast today! Stay tuned." 


img = Image.new('RGB', (1080, 1080), color=(15, 15, 15))
d = ImageDraw.Draw(img)
try:
    
    fnt = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 95)
except:
    fnt = ImageFont.load_default(size=85) 

d.text((540, 540), news_text, fill=(255, 255, 255), anchor="mm", font=fnt)
img.save("post.jpg")


IG_USER_ID = os.getenv('IG_USER_ID')
META_ACCESS_TOKEN = os.getenv('META_ACCESS_TOKEN') 

container_url = f"https://graph.facebook.com/v22.0/{IG_USER_ID}/media"
publish_url = f"https://graph.facebook.com/v22.0/{IG_USER_ID}/media_publish"
image_url = "https://ayush-d-90.github.io/ig_post_bot/post.jpg"


payload = {'image_url': image_url, 'caption': news_text, 'access_token': META_ACCESS_TOKEN}
r1 = requests.post(container_url, data=payload)
res1 = r1.json()
import time 



if "id" in res1:
    creation_id = res1['id']
    print(f"Upload Success! Container ID: {creation_id}. Waiting for Meta to process...")
    
    
    for attempt in range(3):
        time.sleep(30) 
        
        publish_payload = {
            'creation_id': creation_id,
            'access_token': META_ACCESS_TOKEN
        }
        
        r2 = requests.post(publish_url, data=publish_payload)
        res2 = r2.json()
        
        if "id" in res2:
            print(f"FINAL SUCCESS! Post ID: {res2['id']}")
            break 
        else:
            print(f"Attempt {attempt + 1} failed: {res2.get('error', {}).get('message')}")
            if attempt == 2: 
                print("Could not publish after 3 tries.")
                exit(1)
else:
    print(f"FAILED AT UPLOAD: {res1.get('error', {}).get('message')}")
    exit(1)
