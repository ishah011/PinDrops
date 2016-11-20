from flask import Flask
from flask_mysqldb import MySQL
from flask import render_template, request, session, flash, redirect, url_for

import urllib2
import json

app = Flask(__name__)
mysql = MySQL(app)
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'cs411fa2016'
app.config['MYSQL_DB'] = 'imdb'
app.config['MYSQL_HOST'] = 'fa16-cs411-29.cs.illinois.edu'

def geocode(searchString):
    print "GEOCODE FUNCTION START"

    APIurl = "http://free.gisgraphy.com/geocoding/geocode?address={}&format=JSON&from=1&to=10&indent=false".format(urllib.quote_plus(searchString))
    content = urllib2.urlopen(APIurl).read()
    json_data = json.loads(content)

    numFound = json_data["numFound"]
    if numFound is 0
        db.execute("""UPDATE Filmed_In SET latitude = 0, longitude = 0 WHERE location = '{}'""".format(searchString))
        conn.commit()
        return

    lat = json_data["result"][0]["lat"]
    lng = json_data["result"][0]["lng"]

    rv = []
    conn = mysql.connection
    db = conn.cursor()
    db.execute("""SELECT * FROM Filmed_In WHERE location='{}'""".format(searchString))
	rv = db.fetchall()
	if len(rv) > 0:
        print "UPDATING LAT AND LONG WITH VALUES:" + lat + " " + lng
        db.execute("""UPDATE Filmed_In SET latitude = {}, longitude = {} WHERE location = '{}'""".format(lat, lng, searchString))
        conn.commit()
    else:
        print "NO MATCHING LOCATION"

@app.route('/')
def index(store=None):
    return render_template('search.html')

@app.route('/search', methods=['GET','POST'])
def search():
	error = None
	store = []
	advanced1 = ""
	advanced2 = ""
	if request.method == 'POST':
		cur = mysql.connection.cursor()
		if request.form['selection'] == 'Actor':
			fname = request.form['firstName']
			fname = fname.capitalize()
			lname = request.form['lastName']
			lname = lname.capitalize()
			cur.execute("""SELECT m.title, f.location, f.latitude, f.longitude FROM imdb.Movies m LEFT JOIN imdb.Filmed_In f ON f.movie_id = m.id LEFT JOIN imdb.ActedIn a ON a.movie_id = m.id LEFT JOIN imdb.Actors t ON t.actor_id = a.person_id WHERE t.name = '{}, {}'""".format(lname, fname))
#			cur.execute("""SELECT * FROM Actors WHERE name LIKE '%{}, {}%'""".format(lname, fname))
			rv = cur.fetchall()
            repeat = False

            print "Inside the search function, about to attempt geocoding"

            for i in rv:
                    print "Calling GEOCODE"
                    geocode(i[2])
                    repeat = True

            if repeat
                cur.execute("""SELECT m.title, f.location, f.latitude, f.longitude FROM imdb.Movies m LEFT JOIN imdb.Filmed_In f ON f.movie_id = m.id LEFT JOIN imdb.ActedIn a ON a.movie_id = m.id LEFT JOIN imdb.Actors t ON t.actor_id = a.person_id WHERE t.name = '{}, {}'""".format(lname, fname))
    #			cur.execute("""SELECT * FROM Actors WHERE name LIKE '%{}, {}%'""".format(lname, fname))
    			rv = cur.fetchall()

			store = []
			for i in rv[:20]:
				temp = []
				for j in i:
					if type(j) == "string":
						temp.append(str(j.encode('ascii', 'ignore')))
					else:
						temp.append(str(j))
				store.append(": ".join(temp))
			advanced1 = "A map with the returned locations marked will be placed here along with movie recommedations based off of the search query. This is an advanced feature"
			advanced2 = "Graphical data(such as revenue and ratings) about the movies at the marked locations will be placed here. This is an advanced feature"
		elif request.form['selection'] == 'Movie':
		 	movieName = request.form['movieName']
			movieName = movieName.capitalize()
			cur.execute("""SELECT DISTINCT m.title, f.location FROM Filmed_In f, Movies m WHERE m.title LIKE'%{}%' AND f.movie_id = m.id""".format(movieName))
			rv = cur.fetchall()
			store = []
			for i in rv:
				temp = []
				for j in i:
					if type(j) == "string":
						temp.append(str(j.encode('ascii', 'ignore')))
					else:
						temp.append(str(j))
				store.append(": ".join(temp))
			advanced1 = "A map with the returned locations marked will be placed here along with movie recommedations based off of the search query. This is an advanced feature"
                        advanced2 = "Graphical data(such as revenue and ratings) about the movies at the marked locations will be placed here. This is an advanced feature"

		elif request.form['selection'] == 'Location':
			city = request.form['cityName']
			state = request.form['stateName']
			country = request.form['countryName']
			city = city.capitalize()
			state = state.capitalize()
			country = country.capitalize()
			if (country == 'England' or country == 'Scotland' or country == 'Ireland' or country == 'Wales'):
				if country == 'Ireland':
					country = 'Northern Ireland'
				city = city
				state = country
				country = "UK"
			if country == 'Us' or country == 'America' or country == 'US':
				country = 'USA'
			cur.execute("""SELECT title, production_year FROM imdb.Filmed_In f, imdb.Movies m WHERE f.location = "{}, {}, {}" AND f.movie_id = m.id""".format(city, state, country))
			rv = cur.fetchall()
			store = []
			for i in rv[:20]:
				temp = []
				for j in i:
					if type(j) == 'string':
						temp.append(str(j.encode('ascii', 'ignore')))
					else:
						temp.append(str(j))
				store.append(" - ".join(temp))
			advanced1 = "A map with the returned locations marked will be placed here along with movie recommedations based off of the search query. This is an advanced feature"
                        advanced2 = "Graphical data(such as revenue and ratings) about the movies at the marked locations will be placed here. This is an advanced feature"

		else:
		 	error = "Please choose an option below"
        return render_template('search.html', error=error,store=store, advanced1=advanced1, advanced2=advanced2)

@app.route('/add', methods=['GET','POST'])
def add_entry():
    error = None
    if request.method == 'POST':
	rv = []
        conn = mysql.connection
        db = conn.cursor()
	email = request.form['email']
        db.execute("""SELECT * FROM Users WHERE email='{}'""".format(email))
	rv = db.fetchall()
	if len(rv) is 0:
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
