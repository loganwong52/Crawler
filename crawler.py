# import requests
# import cloudscraper
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

import re
import json
from bs4 import BeautifulSoup
from collections import Counter
import traceback

STOP_WORDS = {"the","a","an","and","or","but","in","on","at","to","for","of","with","by","from","up","about","is","are","was","were","be","been","being","have","has","had","do","does","did","will","would","shall","should","can","could","may","might","must","i","you","he","she","it","we","they","me","him","her","us","them","my","your","his","its","our","their","this","that","these","those","am","no","not","all","as","if","more","than","very","just","so","some","such","only","also","&"}

def extract_keywords(text):
    """
    text: combined title, description, & body
    Remove common stop words.
    Finds words with 4+ letters.
    Returns the 10 most frequent.

    """
    if not text:
        return []
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
    filtered = []
    for w in words:
        if w not in STOP_WORDS:
            filtered.append(w)

    top_10_keywords = []
    for word, count in Counter(filtered).most_common(10):
        top_10_keywords.append(word)
    return top_10_keywords

def get_meta(soup, attr, value):
    tag = soup.find("meta", attrs={attr: value})
    if tag and tag.get("content"):
        return tag["content"].strip()
    else:
        return None


def crawl(url):
    # create object to tell Chrome how to behave
    options = Options()
    # run w/o showing a browser window
    options.add_argument("--headless=new")
    # disable Chrome's security sandbox
    options.add_argument("--no-sandbox")
    # tell Chrome to use temporary folders, don't crash in Linux environment
    options.add_argument("--disable-dev-shm-usage")
    # disable GPU
    options.add_argument("--disable-gpu")  
    # disable chrome extentions from loading
    options.add_argument("--disable-extensions")
    # disable setuid sandbox
    options.add_argument("--disable-setuid-sandbox")
    

    # tell website what browser and OS to pretend to be
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")
    
    # download the right ChromeDriver, wrap it in Selenium, and lanuch the browser to remote control it
    print("creating driver", flush=True)
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    print("Driver created", flush=True)
    try:
        # go to the URL
        print(f"Loading {url}", flush=True)
        driver.get(url)
        print("URL Loaded", flush=True)
    except Exception:
        traceback.print_exc()
        raise

    # GRAB the page HTML & close it
    html = driver.page_source
    print("Got page source", flush=True)
    soup = BeautifulSoup(html, "html.parser")
    print("Soup", flush=True)
    driver.quit()
    print("Driver quit", flush=True)


    # title: HTML title tag inside <head>
    title = None
    if soup.title:
        title = soup.title.string.strip()
    
    # description: inside <meta name="description" content="..."> inside <head>.
    description = get_meta(soup, "name", "description")

    # Keywords: meta keywords; Amazon doesn't include this
    keywords = get_meta(soup, "name", "keywords")
    
    # Author: inside <meta name="author" content="...">; not used for product pages like Amazon
    author = get_meta(soup, "name", "author")

    # Open Graph tags; not included by Amazon
    og_title = get_meta(soup, "property", "og:title")
    og_description = get_meta(soup, "property", "og:description")
    og_image = get_meta(soup, "property", "og:image")
    
    # Extract meta description          
    # Remove unecessary tags & Extract text
    for tag in soup(["script", "style", "meta", "noscript"]):
        tag.decompose()
    body = re.sub(r'\s+', ' ', soup.get_text()).strip()
    # BODY: all visible text on a page after removing script/style/meta tags

    # Topics: Generated keywords if keywords is None from title + description + body
    topics = extract_keywords(f"{title or ''} {description or ''} {body}")
    if keywords is None:
        keywords = topics
    # if keywords do exist, they may or may not match topics, so I'll keep both

    return {
        "url": url,
        "title": title,
        "description": description,
        "keywords": keywords,
        "author": author,
        "topics": topics,
        "og:title": og_title,
        "og:description": og_description,
        "og:image": og_image,
        "body": body
    }

if __name__ == "__main__":
    amazon_test_url = "https://www.amazon.com/Cuisinart-CPT-122-Compact-2-Slice-Toaster/dp/B009GQ034C/ref=sr_1_1?s=kitchen&ie=UTF8&qid=1431620315&sr=1-1&keywords=toaster&th=1"
    outdoors_test_url = "https://www.rei.com/blog/camp/how-to-introduce-your-indoorsy-friend-to-the-outdoors/"
    cnn_test_url = "https://www.cnn.com/2025/09/23/tech/google-study-90-percent-tech-jobs-ai"

    url = amazon_test_url
    # url = outdoors_test_url
    # url = cnn_test_url
    result = crawl(url)

    if url == amazon_test_url:
        output_file_name = "amazon_output.txt"
    elif url == outdoors_test_url:
        output_file_name = "outdoors_output.txt"
    elif url == cnn_test_url:
        output_file_name = "cnn_output.txt"
    else:
        output_file_name = "output.txt"

    # Print to terminal
    formatted = json.dumps(result, indent=2, ensure_ascii=False)
    print(formatted)
    
    # Save to file
    with open(output_file_name, "w", encoding="utf-8") as f:
        f.write(formatted)