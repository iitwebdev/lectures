import httplib2
http = httplib2.Http('http-cache')
from hreviewparser.parser import parse_hreviews
from lxml import etree

def get_reviews(urls):
    reviews = []
    urls_seen = set()
    for url in urls:
        reviews.extend(get_reviews_for_url(url, urls_seen))
    return reviews

def get_reviews_for_url(url, seen):
    if url in seen:
        return
    seen.add(url)
    resp, content = http.request(url, "GET")
    html = etree.HTML(content)
    reviews = parse_hreviews(html)
    found = []
    for review in reviews:
        if review.type == 'review':
            # Should use ratings, etc:
            for sub_url in review.item.urls:
                found.extend(get_reviews_for_url(sub_url, seen))
        else:
            found.append(review)
    return found

