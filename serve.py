from sklearn.externals import joblib
import web
from web import form


myform = form.Form(
    form.Textarea("text")
)

render = web.template.render('templates/')

urls = (
    '/(.*)', 'hello'
)
app = web.application(urls, globals())


class hello:
    def GET(self, name):
        form = myform()
        return render.index(form, "")

    def POST(self, name):
        form = myform()
        if form.validates():
            text = form['text'].value
            clf = joblib.load('clf.pkl')
            predicted = clf.predict([text])
            result = predicted[0]
        else:
            result = ""

        return render.index(form, result)


if __name__ == "__main__":
    app.run()