from flask import Flask, jsonify
import requests
import json
import os
from dotenv import load_dotenv
import time

# Load API Keys
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CX = os.getenv("GOOGLE_CX")

if not GOOGLE_API_KEY or not GOOGLE_CX:
    raise ValueError("❌ Missing GOOGLE_API_KEY or GOOGLE_CX. Set them in .env.")

app = Flask(__name__)

# List of job fair-related queries
QUERIES = [
    '"Job Mela" +(apply OR register OR hiring OR career fair) -news -blog',
    '"Recruitment Drive" +(apply OR register OR hiring OR career fair) -news -blog',
    '"Mega Job Fair" +(apply OR register OR hiring OR career fair) -news -blog',
    '"Walk-in Drive" +(apply OR register OR hiring OR career fair) -news -blog',
    '"Job Expo" +(apply OR register OR hiring OR career fair) -news -blog',
    '"Employment Fair" +(apply OR register OR hiring OR career fair) -news -blog',
    '"Career Fair" +(apply OR register OR hiring OR career fair) -news -blog',
]

# Function to get job drive results from Google API
def get_google_search_results(query):
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={GOOGLE_API_KEY}&cx={GOOGLE_CX}"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"❌ Error fetching results for: {query}")
        return []

    data = response.json()
    results = [{"Title": item["title"], "Link": item["link"]} for item in data.get("items", [])]

    return results

# Function to save results in a JSON file
def save_json_file():
    all_results = []

    for query in QUERIES:
        search_results = get_google_search_results(query)
        if search_results:
            all_results.extend(search_results)
        time.sleep(2)  # Add delay to prevent rate limits

    file_path = os.path.join(os.getcwd(), "filtered_job_drives.json")
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(all_results, file, indent=4, ensure_ascii=False)

    print(f"✅ JSON file saved as {file_path}")

@app.route("/search", methods=["GET"])
def search():
    all_results = []

    for query in QUERIES:
        search_results = get_google_search_results(query)
        if search_results:
            all_results.extend(search_results)

    if not all_results:
        return jsonify({"message": "No job drives found!"}), 204

    return jsonify({"data": all_results})

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "running"})

if __name__ == "__main__":
    fetch_on_startup = os.getenv("FETCH_ON_STARTUP", "true").lower() == "true"
    if fetch_on_startup:
        save_json_file()
    app.run(debug=True)
