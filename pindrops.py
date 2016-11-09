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
	store = []
	if request.method == 'POST':
		cur = mysql.connection.cursor()
		if request.form['selection'] == 'Actor':
			fname = request.form['firstName']
			lname = request.form['lastName']
			cur.execute("""SELECT m.title, f.location FROM imdb.Movies m LEFT JOIN imdb.Filmed_In f ON f.movie_id = m.id LEFT JOIN imdb.ActedIn a ON a.movie_id = m.id LEFT JOIN imdb.Actors t ON t.actor_id = a.person_id WHERE t.name = '{}, {}'""".format(lname, fname))
#			cur.execute("""SELECT * FROM Actors WHERE name LIKE '%{}, {}%'""".format(lname, fname))
			rv = cur.fetchall()
			store = []
			for i in rv[:20]:
				temp = []
				for j in i:
					temp.append(str(j))
				store.append(": ".join(temp))
		elif request.form['selection'] == 'Movie':
		 	movieName = request.form['movieName']
			cur.execute("""SELECT DISTINCT m.title, f.location FROM Filmed_In f, Movies m WHERE m.title LIKE'%{}%' AND f.movie_id = m.id""".format(movieName))
			rv = cur.fetchall()
			store = []
			for i in rv:
				temp = []
				for j in i:
					temp.append(j)
				store.append(": ".join(temp))

		elif request.form['selection'] == 'Location':
		 	city = request.form['cityName']
			state = request.form['stateName']
			country = request.form['countryName']
			cur.execute("""SELECT title, production_year FROM imdb.Filmed_In f, imdb.Movies m WHERE f.location = "{}, {}, {}" AND f.movie_id = m.id""".format(city, state, country))
			rv = cur.fetchall()
			store = []
			for i in rv[:20]:
				temp = []
				for j in i:
					temp.append(str(j))
				store.append(" - ".join(temp))
		else:
		 	error = "Please choose an option below"
        return render_template('search.html', error=error,store=store)

@app.route('/add', methods=['GET','POST'])
def add_entry():
    error = None
    if request.method == 'POST':
        conn = mysql.connection
        db = conn.cursor()
	email = request.form['email']
        db.execute("""SELECT * FROM Users WHERE email='{}'""".format(email))
	rv = db.fetchall()
	if rv is None:
		db.execute("INSERT INTO Users(email, password, firstName, lastName) values (%s, %s, %s, %s)",
	        	          (request.form['email'],request.form['password'], request.form['firstName'],request.form['lastName']))
        	conn.commit()
	else:
		error = "User with email "+ str(email)+ " already exists"
		return render_template('signup.html', error=error)
    else:
        return render_template('signup.html', error=error)	
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    loggedin = False
    error = None
    result  = ""
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
		list(rv)
		store = []
		for i in rv:
			store.append(str(i))
		result = ",".join(store)

    return render_template('login.html', error=error, loggedin=loggedin, result=result)

@app.route('/logout')
def logout():
    loggedin = False
    return redirect(url_for('search'))

if __name__ == '__main__':
    app.run(debug=True)
