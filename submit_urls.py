import feedparser
import requests
import json
import os

def submit_urls_to_indexnow(rss_url, api_key, host):
    # Parse the RSS feed
    feed = feedparser.parse(rss_url)
    urls = [entry.link for entry in feed.entries]

    # Prepare the payload
    url_list = {
        "host": host,
        "key": api_key,
        "urlList": urls
    }

    # Submit the URLs to IndexNow
    api_url = 'https://api.indexnow.org/indexnow'
    headers = {'Content-Type': 'application/json'}
    response = requests.post(api_url, headers=headers, data=json.dumps(url_list))

    print(response.status_code)

if __name__ == "__main__":
    rss_url = os.getenv('RSS_URL')
    api_key = os.getenv('INDEXNOW_API_KEY')
    host = os.getenv('HOST')
    submit_urls_to_indexnow(rss_url, api_key, host)
