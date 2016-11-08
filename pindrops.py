from flask import Flask
from flask_mysqldb import MySQL
from flask import render_template, request, session, flash, redirect, url_for

app = Flask(__name__)
mysql = MySQL(app)
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'cs411fa2016'
app.config['MYSQL_DB'] = 'imdb'
app.config['MYSQL_HOST'] = 'fa16-cs411-29.cs.illinois.edu'


@app.route('/')
def index(store=None): 
    current = ""
    cur = mysql.connection.cursor()
    to_exec = "SELECT * FROM Actors WHERE name='Depp, Johnny'"
    cur.execute("""SELECT * FROM Actors WHERE name='Depp, Johnny'""")
    rv = cur.fetchall()
    list(rv)
    store = []
    for i in rv[0]:
        store.append(str(i))
    return render_template('search.html',store=store)

@app.route('/search', methods=['GET','POST'])
def search():
	error = None
	if request.method == 'POST':
		# cur = mysql.connection.cursor()
		if request.form['selection'] == 'Actor':
			print "test"
			# value = request.form['Search']
			# list(value)
			# if len(value) == 2:
			# 	cur.execute("""SELECT * FROM Actors WHERE name LIKE '%{}, {}%'""".format(value[1], value[0]))
			# elif len(value) > 2:
			# 	cur.execute("""SELECT * FROM Actors WHERE name LIKE '%{}, {} {}%'""".format(value[2], value[0], value[1]))
			# else:
			# 	cur.execute("""SELECT * FROM Actors WHERE name = '{}'""".format(value[0]))
		# elif request.form['selection'] == 'Movie':
		# 	#query for movie
		# elif request.form['selection'] == 'Location':
		# 	#query for location
		# else:
		# 	error = "Please choose an option below"
    return render_template('search.html', error=error)

@app.route('/add', methods=['GET','POST'])
def add_entry():
    if request.method == 'POST':
        conn = mysql.connection
        db = conn.cursor()
        db.execute("INSERT INTO Users(email, password, firstName, lastName) values (%s, %s, %s, %s)",
	                  (request.form['email'],request.form['password'], request.form['firstName'],request.form['lastName']))
        conn.commit()
    else:
        return render_template('signup.html')	
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    loggedin = False
    error = None
    if request.method == 'POST':
        email = request.form['email']
		password = request.form['password']
        cur = mysql.connection.cursor()
		cur.execute("""SELECT * FROM Users WHERE email='{}' AND password='{}'""".format(email, password))

		rv = cur.fetchone()
		if(rv is None):
			error = 'Invalid email or password'
	        else:
	            loggedin = True
	            return redirect(url_for('search'))
#    return str(loggedin)
    return render_template('login.html', error=error, loggedin=loggedin)

@app.route('/logout')
def logout():
    loggedin = False
    return redirect(url_for('search'))

if __name__ == '__main__':
    app.run(debug=True)
