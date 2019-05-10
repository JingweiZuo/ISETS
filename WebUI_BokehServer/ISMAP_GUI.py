from werkzeug.utils import secure_filename
from flask import Flask, flash, redirect, render_template, request, session, abort
from bokeh.embed import server_document, components

app = Flask(__name__)

@app.route("/")
def index():
    #script=autoload_server(model=None,app_path="/bokeh-sliders",url="http://localhost:5006")
    script=server_document("http://localhost:5006/ISETS")
    return render_template('hello.html',bokS=script)

if __name__ == '__main__':
    app.run()
