import httpx
import feedparser

key_list = ["title", "link", "description"]

def poll_once() -> list[dict]:

    items = []
    request = httpx.get("https://trumpstruth.org/feed")

    # if request.status_code != 200:
    #     # do something about this

    print(request.status_code)
    print(request.headers['content-type'])
    
    t = request.text
    d = feedparser.parse(t)
    for entry in d.entries:
        data = dict.fromkeys(key_list)
        data["title"] = entry.title
        data["link"] = entry.link
        data["description"] = entry.description
        items.append(data)
    
    return items


