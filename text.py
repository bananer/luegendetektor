import string
import HTMLParser

class MLStripper(HTMLParser.HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

def clean_text(text):
    text = HTMLParser.HTMLParser().unescape(text.decode("cp1252", "ignore"))
    exclude = set(string.punctuation)
    text = strip_tags(text)
    return text.encode("utf-8", "ignore")
