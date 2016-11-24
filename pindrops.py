from __future__ import print_function
from flask import Flask
from flask_mysqldb import MySQL
from flask import render_template, request, session, flash, redirect, url_for, json, jsonify
from flask_debugtoolbar import DebugToolbarExtension 

import sys
import urllib2
import urllib
import json
import googlemaps

app = Flask(__name__)

app.debug = True
app.config['SECRET_KEY'] = 314159265358979
toolbar = DebugToolbarExtension(app)
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


mysql = MySQL(app)
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'cs411fa2016'
app.config['MYSQL_DB'] = 'imdb'
app.config['MYSQL_HOST'] = 'fa16-cs411-29.cs.illinois.edu'
app.secret_key = """p6\x9e\x08B\xe2\x11/\xbd\xd6k\xb7=\xc3\xd6p\x96\x90S\xd4z\x8f\xe2\r"""

def locationAnalysis():
    rv = []
    conn = mysql.connection
    db = conn.cursor()

    print ( 'Entering LOCATION ANALYSIS', file=sys.stderr)

    db.execute("""SELECT location FROM Filmed_In WHERE latitude IS NULL OR latitude = longitude""")
    rv = db.fetchall()

    for row in rv:
        location = row[0]
        elements = location.split(",")
	location = location.replace("'", "''").encode('ascii', 'ignore').decode('ascii')
        if len(elements) > 2:
            countryCode = elements[-1].encode('ascii', 'ignore').decode('ascii').strip().replace("'", "")
            state = elements[-2].encode('ascii', 'ignore').decode('ascii').strip().replace("'", "")
            city = elements[-3].encode('ascii', 'ignore').decode('ascii').strip().replace("'","")
            if countryCode is None or state is None or city is None:
                return
	    print (countryCode, file=sys.stderr)
	    print (state, file=sys.stderr)
	    print (city, file=sys.stderr)
            db = conn.cursor()
            db.execute("""SELECT latitude, longitude FROM FilmingLocationAlt WHERE ISO3 = '{}' AND stateName = '{}' AND city = '{}'""".format(countryCode, state, city))
            locRV = db.fetchall()
            if len(locRV) > 0:
                lat = locRV[0][0]
                lng = locRV[0][1]

                print ( 'UPDATING LAT AND LONG WITH VALUES: ' + str(lat) + ' ' + str(lng) + ' FOR ' + str(location), file=sys.stderr)

                db = conn.cursor()
                db.execute("""UPDATE Filmed_In SET latitude = {}, longitude = {} WHERE location = '{}'""".format(lat, lng, location))
                conn.commit()



def geocode(searchString):
    print ('GEOCODE FUNCTION START', file=sys.stderr)
    #if type(searchString) != "string":
#	return
    if searchString is None:
	return
    try:
    	APIurl = "https://maps.googleapis.com/maps/api/geocode/json?address={}&key=AIzaSyCaGXqswUJlWF3x9IpdEG2DdA-UhUqaAN0".format(urllib.quote_plus(searchString))
    	content = urllib2.urlopen(APIurl).read()
    except:
	print ('SEVER RETURNED EXCEPTION!!!', file=sys.stderr)
	return
    json_data = json.loads(content)

#    numFound = json_data["numFound"]
#    if numFound is 0:
#        db.execute("""UPDATE Filmed_In SET latitude = 0, longitude = 0 WHERE location = '{}'""".format(searchString))
#        conn.commit()
#        return

    rv = []
    conn = mysql.connection
    db = conn.cursor()

    searchString = searchString.replace("'", "''")

    returnStatus = json_data["status"]
    if returnStatus == "ZERO_RESULTS":
	db.execute("""UPDATE Filmed_In SET latitude = 0, longitude = 0 WHERE location = '{}'""".format(searchString))
        conn.commit()
        return

    print ('LAT AND LONG DATA CAPTURED', file=sys.stderr)
    lat = json_data["results"][0]["geometry"]["location"]["lat"]
    lng = json_data["results"][0]["geometry"]["location"]["lng"]

    try:
     	db.execute("""SELECT * FROM Filmed_In WHERE location='{}'""".format(searchString))
    except:
	print('FATAL SQL ERROR', file=sys.stderr)
	return

    rv = db.fetchall()
    if len(rv) > 0:
        print ( 'UPDATING LAT AND LONG WITH VALUES: ' + str(lat) + ' ' + str(lng), file=sys.stderr)
        db.execute("""UPDATE Filmed_In SET latitude = {}, longitude = {} WHERE location = '{}'""".format(lat, lng, searchString))
        conn.commit()
    else:
        print ('NO MATCHING LOCATION', file=sys.stderr)

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

#        		locationAnalysis()

			fname = request.form['firstName']
			fname = fname.capitalize()
			lname = request.form['lastName']
			lname = lname.capitalize()
			cur.execute("""SELECT m.title, f.location, f.latitude, f.longitude FROM imdb.Movies m LEFT JOIN imdb.Filmed_In f ON f.movie_id = m.id LEFT JOIN imdb.ActedIn a ON a.movie_id = m.id LEFT JOIN imdb.Actors t ON t.actor_id = a.person_id WHERE t.name = '{}, {}'""".format(lname, fname))
#			cur.execute("""SELECT * FROM Actors WHERE name LIKE '%{}, {}%'""".format(lname, fname))
			rv = cur.fetchall()
#    		        repeat = False

#           		print ('ENTER SEARCH METHOD', file=sys.stderr)
#         		app.logger.info('Flask toolbar is operational inside search method')

#           		for i in rv:
#				 if i[2] is None:
#                   			 print ('CALLING GEOCODE', file=sys.stderr)
#					 print (i[1], file=sys.stderr)
#                   			 geocode(i[1])
#                   			 repeat = True

#           		if repeat == True:
#               			cur.execute("""SELECT m.title, f.location, f.latitude, f.longitude FROM imdb.Movies m LEFT JOIN imdb.Filmed_In f ON f.movie_id = m.id LEFT JOIN imdb.ActedIn a ON a.movie_id = m.id LEFT JOIN imdb.Actors t ON t.actor_id = a.person_id WHERE t.name = '{}, {}'""".format(lname, fname))
    #			cur.execute("""SELECT * FROM Actors WHERE name LIKE '%{}, {}%'""".format(lname, fname))
#    				rv = cur.fetchall()

			store = []
			for i in rv[:20]:
				temp = []
				for j in i:
					try:
						if type(j) == "string":
							temp.append(str(j.encode('ascii', 'ignore')))
						else:
							temp.append(str(j))
					except:
						advanced1 = "A map with the returned locations marked will be placed here along with movie recommedations based off of the search query. This is an advanced feature"
                        			advanced2 = "Graphical data(such as revenue and ratings) about the movies at the marked locations will be placed here. This is an advanced feature"
						return render_template('search.html', error=error,store=store, advanced1=advanced1, advanced2=advanced2)
				store.append(": ".join(temp))
			advanced1 = "A map with the returned locations marked will be placed here along with movie recommedations based off of the search query. This is an advanced feature yo"
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
					try:
						if type(j) == "string":
							temp.append(str(j.encode('ascii', 'ignore')))
						else:
							temp.append(str(j))
					except:
						advanced1 = "A map with the returned locations marked will be placed here along with movie recommedations based off of the search query. This is an advanced feature"
						advanced2 = "Graphical data(such as revenue and ratings) about the movies at the marked locations will be placed here. This is an advanced feature"
						return render_template('search.html', error=error, store=store, advanced1=advanced1, advanced2=advanced2)
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
					try:
						if type(j) == 'string':
							temp.append(str(j.encode('ascii', 'ignore')))
						else:
							temp.append(str(j))
					except:
						advanced1 = "A map with the returned locations marked will be placed here along with movie recommedations based off of the search query. This is an advanced feature"
						advanced2 = "Graphical data(such as revenue and ratings) about the movies at the marked locations will be placed here. This is an advanced feature"
						return render_template('search.html', error=error,store=store, advanced1=advanced1, advanced2=advanced2)
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
		session['logged_in'] = True
#        	loggedin = True
		list(rv)
		store = []
		for i in rv:
			store.append(str(i))
		result = ",".join(store)
		return redirect(url_for('search'))

    return render_template('login.html', error=error, loggedin=loggedin, result=result)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('search'))


if __name__ == '__main__':
    app.run(debug=True)
