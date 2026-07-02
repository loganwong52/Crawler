from flask import Flask, request, jsonify
import requests, re
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/crawl')
def crawl():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    headers = {"User-Agent": "Mozilla/5.0 (compatible; MetaCrawler/1.0)"}
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    title = soup.title.string.strip() if soup.title else None
    desc_tag = soup.find("meta", attrs={"name": "description"})
    description = desc_tag["content"].strip() if desc_tag and desc_tag.get("content") else None

    for tag in soup(["script", "style", "meta", "noscript"]):
        tag.decompose()
    body_text = re.sub(r'\s+', ' ', soup.get_text()).strip()[:2000]

    return jsonify({
        "url": url,
        "title": title,
        "description": description,
        "body": body_text
    })

if __name__ == '__main__':
    app.run()