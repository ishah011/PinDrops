from flask import Flask
from flask import render_template

@app.route('/index/')
def index:
	rv = [1,2,3,4,5,6,7,8,9,10]
	return render_template('index.html')