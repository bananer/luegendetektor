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
    texts.append(clean_text(text))
    labels.append("fake" if fake else "real")

X_train, X_test, y_train, y_test = train_test_split(texts, labels, test_size=0.1, random_state=1337)

estimator = SVR(kernel="linear")

forest = ExtraTreesClassifier(n_estimators=250,
                              random_state=1337)

stop_words = ["daãÿ", "dass", "ja", "titanic"]

vect = CountVectorizer(analyzer="word", token_pattern=r"(?u)\b[a-zA-Z]{2,}\b", stop_words=stop_words)

text_clf = Pipeline([
    ('vect', vect),
    ('tfidf', TfidfTransformer(use_idf=True)),
    #('rfe', RFE(estimator, 5, step=1)),
    #('forest', forest),
    #('clf', MultinomialNB()),
    ('clf', SGDClassifier(loss='hinge')),
])


clf = text_clf.fit(X_train, y_train)

features = vect.get_feature_names()

#importances = forest.feature_importances_
#std = np.std([tree.feature_importances_ for tree in forest.estimators_],
#             axis=0)
#indices = np.argsort(importances)[::-1]

# Print the feature ranking
#print("Feature ranking:")

#for f in range(10):
#    print("%d. feature %s (%f)" % (f + 1, features[indices[f]], importances[indices[f]]))

predicted = clf.predict(X_test)
#print "score: ", clf.score(y_test, X_test)
print metrics.classification_report(y_test, predicted, target_names=["fake", "real"])

docs_new = [
    "Martin Schulz ist toll", "die inhalte des bums und newsportals stern de leben", 'zdf titanic', "quelle", "2017"
]
#X_new_counts = count_vect.transform(docs_new)
#X_new_tfidf = tfidf_transformer.transform(X_new_counts)
predicted = clf.predict(docs_new)


for doc, category in zip(docs_new, predicted):
    print('%s => %r' % (category, doc))

predicted = clf.predict(X_test[0:20])

for doc, category in zip(X_test, predicted):
    print('%s => %r' % (category, doc))

joblib.dump(clf, 'clf.pkl')