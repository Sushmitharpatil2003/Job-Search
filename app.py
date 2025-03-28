from flask import Flask, jsonify
import requests
import json
import os
import re
import time
from dotenv import load_dotenv

# Load API Keys
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CX = os.getenv("GOOGLE_CX")

if not GOOGLE_API_KEY or not GOOGLE_CX:
    raise ValueError("❌ Missing GOOGLE_API_KEY or GOOGLE_CX. Set them in .env.")

app = Flask(__name__)

# Queries targeting upcoming job fairs
QUERIES = [
    "Job Mela 2024 venue date apply register",
    "Recruitment Drive 2024 venue date apply register",
    "Mega Job Fair 2024 venue date apply register",
    "Walk-in Drive 2024 venue date apply register",
    "Job Expo 2024 venue date apply register",
    "Employment Fair 2024 venue date apply register",
    "Career Fair 2024 venue date apply register",
]

# Regular expression patterns to extract dates and venues
DATE_PATTERN = r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}\b"
VENUE_PATTERN = r"\b(?:at|in|venue[:\s])\s*([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)"

# Function to fetch results from Google API
def get_google_search_results(query):
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={GOOGLE_API_KEY}&cx={GOOGLE_CX}"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"❌ Error fetching results for: {query}")
        return []

    data = response.json()
    results = []
    
    for item in data.get("items", []):
        title = item["title"]
        snippet = item["snippet"]  # Summary of the page
        link = item["link"]

        # Extract date and venue from snippet
        date_match = re.search(DATE_PATTERN, snippet)
        venue_match = re.search(VENUE_PATTERN, snippet)

        event = {
            "Title": title,
            "Link": link,
            "Date": date_match.group(0) if date_match else "Unknown",
            "Venue": venue_match.group(1) if venue_match else "Unknown",
        }

        results.append(event)

    return results

# Function to save job fairs in JSON
def save_json_file():
    upcoming_events = []

    for query in QUERIES:
        search_results = get_google_search_results(query)
        if search_results:
            upcoming_events.extend(search_results)
        time.sleep(2)  # Prevent API rate limits

    file_path = os.path.join(os.getcwd(), "job_fairs_with_dates.json")
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(upcoming_events, file, indent=4, ensure_ascii=False)

    print(f"✅ Upcoming job fairs saved in {file_path}")

@app.route("/search", methods=["GET"])
def search():
    upcoming_events = []

    for query in QUERIES:
        search_results = get_google_search_results(query)
        if search_results:
            upcoming_events.extend(search_results)

    if not upcoming_events:
        return jsonify({"message": "No upcoming job fairs found!"}), 204

    return jsonify({"data": upcoming_events})

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "running"})

if __name__ == "__main__":
    fetch_on_startup = os.getenv("FETCH_ON_STARTUP", "true").lower() == "true"
    if fetch_on_startup:
        save_json_file()
    app.run(debug=True)
