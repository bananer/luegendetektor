

from lxml import html
import requests
from sklearn.externals import joblib
from db import get_db
import json


db = get_db()
cursor = db.cursor()
cursor.execute ("SELECT VERSION()")
row = cursor.fetchone ()
print "server version:", row[0]

cursor.execute('SET NAMES utf8;')
cursor.execute('SET CHARACTER SET utf8;')
cursor.execute('SET character_set_connection=utf8;')

fake_news = []
real_news = []


def train_titanic():

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
            txt = t.text_content().strip()

            if len(txt) > 1000:
                fake_news.append(txt)


def train_br24():
    for x in range(3, 10):
        doc = requests.get("https://br24-backend-hackathon.br.de/api/v4/news?limit=1000&page={}".format(x))
        j = json.loads(doc.content)['data']
        for article in j:
            if article['articleType'] == "news_text":
                real_news.append(article['text'])


train_br24()


for f in fake_news:
    cursor.execute("INSERT INTO news (text, fake) VALUES (%s, 1)", (f.encode('utf-8'),))

for r in real_news:
    cursor.execute("INSERT INTO news (text, fake) VALUES (%s, 0)", (r.encode('utf-8'),))

# commit your changes
db.commit()


#joblib.dump(fake_news, 'fake_news.pkl')