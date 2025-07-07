from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse, urljoin
import os

app = Flask(__name__)

def extract_metadata(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers, timeout=10)
    final_url = res.url  # Handle redirects
    soup = BeautifulSoup(res.text, 'html.parser')

    def meta_content(name):
        tag = soup.find("meta", property=name) or soup.find("meta", attrs={"name": name})
        return tag["content"].strip() if tag and "content" in tag.attrs else None

    def extract_images():
        og_image = meta_content("og:image")
        if og_image:
            return [og_image]
        # Fallback to first <img>
        img_tag = soup.find("img")
        if img_tag and "src" in img_tag.attrs:
            return [urljoin(final_url, img_tag["src"])]
        return []

    parsed = urlparse(final_url)

    return {
        "title": soup.title.string.strip() if soup.title and soup.title.string else meta_content("og:title"),
        "description": meta_content("description") or meta_content("og:description"),
        "images": extract_images(),
        "url": final_url
    }

@app.route("/metadata", methods=["POST"])
def metadata():
    data = request.json
    url = data.get("url")
    if not url:
        return jsonify({"error": "Missing 'url' in request body"}), 400
    try:
        result = extract_metadata(url)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=["GET"])
def index():
    return "👋 Metadata API is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
