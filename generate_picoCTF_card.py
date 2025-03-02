import requests
from PIL import Image, ImageDraw, ImageFont
import os

# Replace this with your picoCTF username
USERNAME = "rugbedbugg"

# API URL for fetching user stats
API_URL = f"https://play.picoctf.org/api/stats/{USERNAME}"

# Fetch data from picoCTF
response = requests.get(API_URL)
if response.status_code == 200:
    data = response.json()
    score = data.get("score", "N/A")
    rank = data.get("rank", "N/A")

    img = Image.new("RGB", (600, 200), color=(0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Load a font (Make sure you have Arial.ttf or update the path)
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  
    font = ImageFont.truetype(font_path, 40)

    draw.text((50, 50), f"picoCTF Progress", font=font, fill=(255, 255, 255))
    draw.text((50, 100), f"Score: {score}", font=font, fill=(0, 255, 0))
    draw.text((50, 150), f"Rank: {rank}", font=font, fill=(0, 255, 255))

    # Save the image
    img.save("picoCTF-progress.png")

    print("✅ Progress card updated successfully!")
else:
    print("⚠️ Failed to fetch data from picoCTF API")
