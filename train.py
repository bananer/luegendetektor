# coding=utf-8

from lxml import html
import requests
from sklearn.externals import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_extraction.text import CountVectorizer
import HTMLParser
import string
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn import metrics
from sklearn.feature_selection import VarianceThreshold
from sklearn.linear_model import SGDClassifier

from text import clean_text
from db import get_db

from sklearn.feature_selection import RFE
from sklearn.svm import SVR
from sklearn.ensemble import ExtraTreesClassifier


db = get_db()
cursor = db.cursor()
cursor.execute("SELECT text, fake FROM news")

data = cursor.fetchall()

texts = []
labels = []


for(text, fake) in data:
    texts.append(text)
    labels.append("fake" if fake else "real")

validate = False

if validate:
    X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.3, random_state=1337)
else:
    X_train = texts
    X_test = []
    y_train = labels
    y_test = []

estimator = SVR(kernel="linear")


stop_words = [
    "daãÿ", "dass", "ja", "titanic", "dpo", "shutterstock", "ssi", "dan", "was", "man", "ich",
    "foto", "wenn", "doch", "gar", "mir", "sie", "nicht", "so", "sich", "er", "es", "postillon",
    "fotolia", "cc", "by", "die", "der", "und", "in", "das", "zu", "den", "mit", "ist", "ein",
    "von", "auf", "eine", "im", "dem", "auch", "als", "wie", "an", "noch", "aus", "des", "hat",
    "aber", "nach", "oder", "werden", "nur", "einen", "bei", "um", "einer", "einem", "wird", "wir",
    "war", "haben", "sind", "vor", "schon", "mehr", "sein", "dann", "am", "zum", "kann", "immer",
    "wieder", "da", "durch", 'habe', 'mal', 'jetzt', 'seine', 'hatte', 'bis', 'zur', 'nun', 'weil',
    'sei', 'gegen', 'heute', 'denn', 'unter', 'soll', 'alle', 'ihre', 'will', 'diese', 'ihr', 'keine',
    'uns', 'hier', 'seiner', 'wurde', 'ganz', 'dieser', 'alles', 'selbst', 'bereits', 'mich', 'wer',
    "vom", "damit", "seit", "ihm", "eines", "gibt", "wo", "ihn", "ab", "ob", "ihnen", "kein", "seinem",
    "ihren", "vom", "wurden", "gibt", "seien", "sa", "fed", "com", "na", "picture", "control",
    "direktlink", "kurtchen", "alliance"
]


reals = []
fakes = []
if validate:
    for t, f in zip(texts, labels):
        if f == "fake":
            fakes.append(t)
        else:
            reals.append(t)

def most_freq(texts):
    v = CountVectorizer(analyzer="word", token_pattern=r"(?u)\b[a-zA-Z]{2,}\b", binary=True, stop_words=stop_words)
    res = v.fit_transform(texts)
    fterms = sorted(zip(v.get_feature_names(), np.asarray(res.sum(axis=0)).ravel()), key=lambda idx: idx[1], reverse=True)[:50]
    return fterms

if validate:
    print "fake most freq: ", most_freq(fakes)
    print "real most freq: ", most_freq(reals)

vect = CountVectorizer(analyzer="word", token_pattern=r"(?u)\b[a-zA-Z]{2,}\b", stop_words=stop_words)


#forest = ExtraTreesClassifier(n_estimators=10,
#                              random_state=1337)
#xclf = forest
xclf = SGDClassifier(loss='hinge', penalty='elasticnet', n_jobs=-1)
text_clf = Pipeline([
    ('vect', vect),
    ('tfidf', TfidfTransformer(use_idf=True)),
    ('clf', xclf),
])

print "Classification start..."
clf = text_clf.fit(X_train, y_train)

features = vect.get_feature_names()

if validate:
    predicted = clf.predict(X_test)
    print metrics.classification_report(y_test, predicted, target_names=["fake", "real"])

    docs_new = [
        "Martin Schulz ist toll", "die inhalte des bums und newsportals stern de leben", 'zdf titanic', "quelle", "2017"
    ]
    predicted = clf.predict(docs_new)


    for doc, category in zip(docs_new, predicted):
        print('%s => %r' % (category, doc))

    predicted = clf.predict(X_test[0:20])

    for doc, category in zip(X_test, predicted):
        print('%s => %r' % (category, doc))

joblib.dump(clf, 'clf.pkl')