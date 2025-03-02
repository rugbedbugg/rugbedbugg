import requests
from PIL import Image, ImageDraw, ImageFont

# Replace with your picoCTF username
USERNAME = "rugbedbugg"

# API endpoint for picoCTF user stats
API_URL = f"https://api.picoctf.org/stats/user/{USERNAME}"

def fetch_picoctf_progress(username):
    response = requests.get(f"https://api.picoctf.org/stats/user/{username}")
    if response.status_code == 200:
        return response.json()
    else:
        print("❌ Error fetching data. Check username or API availability.")
        return None

def create_progress_card(data):
    username = data.get("username", "Unknown")
    score = data.get("score", 0)
    rank = data.get("rank", "N/A")
    categories = data.get("categories", {})

    # Create a blank image
    img = Image.new("RGB", (652, 300), color=(10, 10, 35))
    draw = ImageDraw.Draw(img)

    # Load font
    try:
        font = ImageFont.truetype("arial.ttf", 30)
    except IOError:
        font = ImageFont.load_default()

    # Draw text
    draw.text((20, 20), f"🏴‍☠️ picoCTF Progress Card", font=font, fill=(255, 255, 255))
    draw.text((20, 70), f"👤 User: {username}", font=font, fill=(200, 200, 255))
    draw.text((20, 110), f"🏆 Score: {score}", font=font, fill=(255, 215, 0))
    draw.text((20, 150), f"📊 Rank: {rank}", font=font, fill=(255, 69, 0))

    y_offset = 200
    for category, stats in categories.items():
        solved = stats.get("solved", 0)
        total = stats.get("total", 0)
        percent = round((solved / total) * 100) if total > 0 else 0
        draw.text((20, y_offset), f"📂 {category}: {solved}/{total} ({percent}%)", font=font, fill=color_code(percent))
        y_offset += 40

    # Save the image
    img.save("picoCTF-progress.png")

def color_code(percent):
    """Returns color based on percentage."""
    if percent >= 75:
        return (50, 205, 50)  # Green
    elif percent >= 50:
        return (255, 255, 0)  # Yellow
    elif percent >= 25:
        return (255, 140, 0)  # Orange
    else:
        return (255, 0, 0)  # Red

if __name__ == "__main__":
    data = fetch_picoctf_progress(USERNAME)
    if data:
        create_progress_card(data)
