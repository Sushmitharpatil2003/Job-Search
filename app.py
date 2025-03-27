from flask import Flask, jsonify
import requests
import json
import os
from dotenv import load_dotenv

# Load API Keys
load_dotenv()
SERP_API_KEY = os.getenv("SERP_API_KEY")  # Get from SerpAPI

app = Flask(__name__)

# List of multiple queries related to job fairs
QUERIES = [
    "Job Mela 2025 India",
    "Campus Recruitment 2025",
    "Walk-in Drive for Freshers 2025",
    "Mega Job Fair 2025",
    "Upcoming Job Drives in India",
    "Government Job Mela 2025",
]

# Function to get search results from SerpAPI
def get_search_results(query):
    url = f"https://serpapi.com/search.json?q={query}&api_key={SERP_API_KEY}"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"❌ Error fetching results for: {query}")
        return []

    data = response.json()
    results = [{"Query": query, "Title": result["title"], "Link": result["link"]} for result in data.get("organic_results", [])]

    return results

# Function to save JSON file
def save_json_file():
    all_results = []

    for query in QUERIES:
        search_results = get_search_results(query)
        if search_results:
            all_results.extend(search_results)

    file_path = os.path.join(os.getcwd(), "job_mela_results.json")  # Save in current directory
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(all_results, file, indent=4, ensure_ascii=False)

    print(f"✅ JSON file saved as {file_path}")

@app.route("/search", methods=["GET"])
def search():
    all_results = []

    for query in QUERIES:
        search_results = get_search_results(query)
        if search_results:
            all_results.extend(search_results)

    if not all_results:
        return jsonify({"message": "No results found!"})

    return jsonify({"data": all_results})

if __name__ == "__main__":
    save_json_file()  # Auto-fetch job mela details on startup
    app.run(debug=True)
