

from lxml import html
import requests
from sklearn.externals import joblib
from db import get_db
import json

import requests_cache
requests_cache.install_cache()

db = get_db()
cursor = db.cursor()
cursor.execute ("SELECT VERSION()")
row = cursor.fetchone ()
print "server version:", row[0]

cursor.execute('SET NAMES utf8;')
cursor.execute('SET CHARACTER SET utf8;')
cursor.execute('SET character_set_connection=utf8;')


def insert(text, source, fake):
    text = text.strip()
    if len(text) > 1000:
        print ">>> ", text[0:200]
        cursor.execute("INSERT INTO news (text, source, fake) VALUES (%s, %s, %s)", (
            text.encode('utf-8'),
            source.encode('utf-8'),
            1 if fake else 0
        ))
    else:
        print "--- (skipped)"


def scrape_titanic():

    fake_sources = [
    ]

    for x in range(101, 1000):
        fake_sources.append({
            'url': "http://www.titanic-magazin.de/newsticker/seite/{}/".format(x),
            'text_selector': ".tt_news-bodytext"
        })

    for s in fake_sources:
        page = requests.get(s['url'])
        tree = html.fromstring(page.content)

        texts = tree.cssselect(s['text_selector'])
        for t in texts:
            txt = t.text_content()

            insert(txt, "titanic", True)


def scrape_br24():
    for x in range(10, 12):
        doc = requests.get("https://br24-backend-hackathon.br.de/api/v4/news?limit=1000&page={}".format(x))
        j = json.loads(doc.content)['data']
        for article in j:
            if article['articleType'] == "news_text":
                insert(article['text'], "br24", False)



def scrape_postillion():
    urls = set()
    for x in range(1, 13):
        page = requests.get("http://www.der-postillon.com/search?updated-max=2015-{}-01T00:00:00%2B00:00&max-results=50".format(x))
        tree = html.fromstring(page.content)
        links = tree.cssselect(".post-title.entry-title a")
        for l in links:
            url = l.attrib['href']
            if len(url) > 0:
                urls.add(url)

    for url in urls:
        page = requests.get(url)
        tree = html.fromstring(page.content)
        text = tree.cssselect('.post-body')[0]
        insert(text.text_content(), "postillion", 1)


scrape_br24()


# commit your changes
db.commit()


#joblib.dump(fake_news, 'fake_news.pkl')