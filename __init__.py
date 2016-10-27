from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route('/index/')
def index(rv=None):
	rv = [1,2,3,4,5,6,7,8,9,10]
	return render_template('index.html',rv=rv)
