from sklearn.externals import joblib
import web
from web import form


myform = form.Form(
    form.Textarea("text")
)

render = web.template.render('templates/')

urls = (
    '/(.*)', 'hello'
	'/images/(.*)', 'images' #this is where the image folder is located....
)
app = web.application(urls, globals())


class hello:
    def GET(self, name):
        form = myform()
        return render.index(form, "", "")

    def POST(self, name):
        form = myform()
        text = ""
        result = ""
        if form.validates():
            text = form['text'].value
            clf = joblib.load('clf.pkl')
            predicted = clf.predict([text])
            result = predicted[0]

        return render.index(form, text, result)
		
import os
class images:
    def GET(self,name):
        ext = name.split(".")[-1] # Gather extension

        cType = {
            "png":"images/png",
            "jpg":"images/jpeg"          }

        if name in os.listdir('images'):  # Security
            web.header("Content-Type", cType[ext]) # Set the Header
            return open('images/%s'%name,"rb").read() # Notice 'rb' for reading images
        else:
            raise web.notfound()


if __name__ == "__main__":
    app.run()