from flask import Flask, request, jsonify, render_template
from crawler import crawl as do_crawl


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/crawl')
def crawl():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "No URL provided"}), 400
    try:
        return jsonify(do_crawl(url))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)