import requests
import json
import os

# 🔹 Replace with your picoCTF username
USERNAME = "rugbedbugg"

# API URL
API_URL = f"https://play.picoctf.org/api/stats/{USERNAME}"

# Fetch user stats
response = requests.get(API_URL)

if response.status_code == 200:
    data = response.json()

    # Extract relevant data
    total_score = data.get("score", "N/A")
    rank = data.get("rank", "N/A")
    challenges = data.get("solved_challenges", [])

    # Generate Markdown Table
    table = "| Challenge Name | Points Earned | Status |\n"
    table += "|---------------|--------------|--------|\n"

    for challenge in challenges:
        name = challenge.get("name", "Unknown")
        points = challenge.get("points", "N/A")
        status = "✅ Completed"
        table += f"| {name} | {points} | {status} |\n"

    # Final markdown content
    markdown_content = f"""
## 🏆 picoCTF Progress

{table}

🔹 **Total Score:** {total_score}  
🔹 **Rank:** #{rank}  
🔹 **User:** [{USERNAME}](https://play.picoctf.org/users/{USERNAME})
"""

    # Read current README
    with open("README.md", "r", encoding="utf-8") as file:
        readme = file.readlines()

    # Find the picoCTF section and replace it
    start_marker = "## 🏆 picoCTF Progress"
    start_index = next((i for i, line in enumerate(readme) if start_marker in line), None)

    if start_index is not None:
        readme = readme[:start_index]  # Remove old section

    # Append updated content
    readme.append(markdown_content)

    # Write back to README
    with open("README.md", "w", encoding="utf-8") as file:
        file.writelines(readme)

    print("✅ picoCTF progress updated successfully.")

else:
    print(f"❌ Failed to fetch data. Status Code: {response.status_code}")
