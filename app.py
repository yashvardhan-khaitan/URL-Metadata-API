from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse, urljoin
import os

app = Flask(__name__)

def extract_metadata(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(res.text, 'html.parser')

    def meta_content(name):
        tag = soup.find("meta", property=name) or soup.find("meta", attrs={"name": name})
        return tag["content"].strip() if tag and "content" in tag.attrs else None

    parsed = urlparse(url)
    # base_url = f"{parsed.scheme}://{parsed.netloc}"

    # favicon_tag = soup.find("link", rel=lambda x: x and "icon" in x.lower())
    # favicon = urljoin(base_url, favicon_tag["href"]) if favicon_tag and "href" in favicon_tag.attrs else None

    return {
        "title": soup.title.string.strip() if soup.title else meta_content("og:title"),
        "description": meta_content("description") or meta_content("og:description"),
        "images": [meta_content("og:image")] if meta_content("og:image") else [],
        "sitename": meta_content("og:site_name") or parsed.netloc,
        # "favicon": favicon,
        # "domain": parsed.netloc,
        "url": url
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
