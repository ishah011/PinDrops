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
import plotly.plotly as py
import plotly.graph_objs as go
import plotly
import plotly.tools as tls

plotly.tools.set_credentials_file(username='PinDroppers', api_key='4c9lIQK4LJbxCvxvDCM6')

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

def getRevenue(movieList):
    rvRevs = []
    rvNames = []
    conn = mysql.connection
    lookup = {}
    searchString = ""

    for movie in movieList:
        searchString = searchString + str(movie[0]) + " OR movie_id = "
        lookup[movie[0]] = movie[1]

    searchString = searchString[:-15]

    db = conn.cursor()
    db.execute("""SELECT info, movie_id FROM `movie_info` WHERE (movie_id = {}) AND info_type_id = 107 ORDER BY movie_id ASC""".format(searchString))
    result = db.fetchall()
    if len(result) > 0:
        for rtRev in result:
            rev = rtRev[0]
            name = rtRev[1]
            if rev is None:
                continue
            else:
		rev = rev.replace(",", "")
		rev = rev[0] + " " + rev[1:]
		#rev = rev.encode('ascii', 'ignore').decode('ascii')
		#print (rev, file=sys.stderr)
		rev = [int(s) for s in rev.split(" ") if s.isdigit()]
		#print (rev, file=sys.stderr)

                rvRevs.append(rev[0])
                rvNames.append(lookup[name])
    else:
        rvRevs.append(-1)
        rvNames.append('NA')

    rv = [rvNames, rvRevs]
    
    return rv

def getAdmissions(movieList):
    rvRevs = []
    rvNames = []
    conn = mysql.connection
    lookup = {}
    searchString = ""

    for movie in movieList:
        searchString = searchString + str(movie[0]) + " OR movie_id = "
        lookup[movie[0]] = movie[1]

    searchString = searchString[:-15]

    db = conn.cursor()
    db.execute("""SELECT info, movie_id FROM `movie_info` WHERE (movie_id = {}) AND info_type_id = 110 ORDER BY movie_id ASC""".format(searchString))
    result = db.fetchall()
    if len(result) > 0:
        for rtRev in result:
            rev = rtRev[0]
            name = rtRev[1]
            if rev is None:
                continue
            else:
		rev = rev.replace(",", "")
		#rev = rev.encode('ascii', 'ignore').decode('ascii')
		#print (rev, file=sys.stderr)
		rev = [int(s) for s in rev.split(" ") if s.isdigit()]
		#print (rev, file=sys.stderr)

                rvRevs.append(rev[0])
                rvNames.append(lookup[name])
    else:
        rvRevs.append(-1)
        rvNames.append('NA')

    rv = [rvNames, rvRevs]
    
    return rv

def getBudgets(movieList):
    rvRevs = []
    rvNames = []
    conn = mysql.connection
    lookup = {}
    searchString = ""

    for movie in movieList:
        searchString = searchString + str(movie[0]) + " OR movie_id = "
        lookup[movie[0]] = movie[1]

    searchString = searchString[:-15]

    db = conn.cursor()
    db.execute("""SELECT info, movie_id FROM `movie_info` WHERE (movie_id = {}) AND info_type_id = 105 ORDER BY movie_id ASC""".format(searchString))
    result = db.fetchall()
    if len(result) > 0:
        for rtRev in result:
            rev = rtRev[0]
            name = rtRev[1]
            if rev is None:
                continue
            else:
		rev = rev.replace(",", "")
		rev = rev[0] + " " + rev[1:]
		#rev = rev.encode('ascii', 'ignore').decode('ascii')
		#print (rev, file=sys.stderr)
		rev = [int(s) for s in rev.split(" ") if s.isdigit()]
		#print (rev, file=sys.stderr)

                rvRevs.append(rev[0])
                rvNames.append(lookup[name])
    else:
        rvRevs.append(-1)
        rvNames.append('NA')

    rv = [rvNames, rvRevs]
    
    return rv

def getGenres(movieList):
    rvCount = []
    rvGenres = []
    conn = mysql.connection
    lookup = {}
    searchString = ""

    for movie in movieList:
        searchString = searchString + str(movie[0]) + " OR movie_id = "

    searchString = searchString[:-15]

    db = conn.cursor()
    db.execute("""SELECT info FROM `movie_info` WHERE (movie_id = {}) AND info_type_id = 3 ORDER BY movie_id ASC""".format(searchString))
    result = db.fetchall()
    if len(result) > 0:
        for rtRev in result:
            lookup[rtRev[0]] = lookup.get(rtRev[0], 0) + 1
    else:
        rvCount.append(-1)
        rvGenres.append('NA')

    for key, value in lookup.iteritems():
        rvGenres.append(str(key))
        rvCount.append(value)

    rv = [rvGenres, rvCount]
    
    return rv


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
	somedict = {}
	admissions = ""
	revenue = ""
	budget = ""
	genres = ""
	if request.method == 'POST':
		cur = mysql.connection.cursor()
		if request.form['selection'] == 'Actor':

#        		locationAnalysis()

			fname = request.form['firstName']
			fname = fname.capitalize()
			lname = request.form['lastName']
			lname = lname.capitalize()
			cur.execute("""SELECT m.id, m.title, f.location, f.latitude, f.longitude FROM imdb.Movies m LEFT JOIN imdb.Filmed_In f ON f.movie_id = m.id LEFT JOIN imdb.ActedIn a ON a.movie_id = m.id LEFT JOIN imdb.Actors t ON t.actor_id = a.person_id WHERE t.name = '{}, {}'""".format(lname, fname))
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

			name = []
			xcoord = []
			ycoord = []
			for i in rv[:20]:
				count = 1
				for j in i:
					try:
						if type(j) == "string":
							if count%4 is 0:
								xcoord.append(j)
								count += 1
							elif count%5 is 0:
								ycoord.append(j)
								count += 1
							elif (count+2)%3 is 0:
								count += 1
								continue
							else:
								name.append(str(j.encode('ascii', 'ignore')))
								count += 1
			 			else:
			 				if count%3 is 0:
								xcoord.append(j)
								count += 1
							elif count%4 is 0:
								ycoord.append(j)
								count += 1
							elif (count+2)%3 is 0:
								count += 1
								continue
							else:
								name.append(str(j))
								count += 1
			 		except:
			 			somedict={		"name"		:	[i for i in name],
									"xcoord"	:	[x for x in xcoord],
									"ycoord"	:	[y for y in ycoord]
						}
						dat = getAdmissions(rv)
						data = [go.Bar(
			        			x= dat[0],
			           			y= dat[1]
			    			)]
						layout = go.Layout(
						    title='Admissions',
						)
						fig = go.Figure(data=data, layout=layout)
						admissions = tls.get_embed(py.plot(fig, filename='admissions', fileopt = 'overwrite'))
						
						dat = getRevenue(rv)
						data = [go.Bar(
							x= dat[0],
							y= dat[1]
						)]
						layout = go.Layout(
						    title='Revenue',
						)
						revenue = tls.get_embed(py.plot(fig, filename='revenue', fileopt = 'overwrite'))

						dat = getBudgets(rv)
						data = [go.Bar(
			        			x= dat[0],
			           			y= dat[1]
			    		)]
			    		layout = go.Layout(
						    title='Budgets',
						)
						budget = tls.get_embed(py.plot(fig, filename='budget', fileopt='overwrite'))

						dat = getGenres(rv)
						fig = {
			    			'data': [{'labels': dat[0],
			            	'values': dat[1],
			            	'type': 'pie'}],
			    			'layout': {'title': 'Genres filmed'}
			     		}
						genres = tls.get_embed(py.plot(fig, filename='genres', fileopt='overwrite'))

						admissions = tls.get_embed(py.plot(data, filename='admissions', fileopt = 'overwrite'))
						advanced1 = "A map with the returned locations marked will be placed here along with movie recommedations based off of the search query. This is an advanced feature"
			 			#advanced2 = "Graphical data(such as revenue and ratings) about the movies at the marked locations will be placed here. This is an advanced feature"
			 			return render_template('search.html', error=error,store=name, advanced1=advanced1, advanced2=advanced2, somedict=somedict, admissions=admissions, revenue=revenue, budget=budget, genres=genres)
			store = name
			
			#JSON FOR GOOGLE MAPS MARKERS
			somedict={		"name"		:	[i for i in name],
						"xcoord"	:	[x for x in xcoord],
						"ycoord"	:	[y for y in ycoord]
			}

			#CODE TO RETRIEVE DATA GRAPHS
			dat = getAdmissions(rv)
			data = [go.Bar(
        			x= dat[0],
           			y= dat[1]
    			)]
			layout = go.Layout(
			    title='Admissions',
			)
			fig = go.Figure(data=data, layout=layout)
			admissions = tls.get_embed(py.plot(fig, filename='admissions', fileopt = 'overwrite'))
			
			dat = getRevenue(rv)
			data = [go.Bar(
				x= dat[0],
				y= dat[1]
			)]
			layout = go.Layout(
			    title='Revenue',
			)
			revenue = tls.get_embed(py.plot(fig, filename='revenue', fileopt = 'overwrite'))

			dat = getBudgets(rv)
			data = [go.Bar(
        			x= dat[0],
           			y= dat[1]
    		)]
    		layout = go.Layout(
			    title='Budgets',
			)
			budget = tls.get_embed(py.plot(fig, filename='budget', fileopt='overwrite'))

			dat = getGenres(rv)
			fig = {
    			'data': [{'labels': dat[0],
            	'values': dat[1],
            	'type': 'pie'}],
    			'layout': {'title': 'Genres filmed'}
     		}
			genres = tls.get_embed(py.plot(fig, filename='genres', fileopt='overwrite'))



			advanced1 = "A map with the returned locations marked will be placed here along with movie recommedations based off of the search query. This is an advanced feature"
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
						return render_template('search.html', error=error, store=store, advanced1=advanced1, advanced2=advanced2, somedict=somedict, admissions=admissions, revenue=revenue, budget=budget, genres=genres)
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
			cur.execute("""SELECT m.id, title, production_year FROM imdb.Filmed_In f, imdb.Movies m WHERE f.location = "{}, {}, {}" AND f.movie_id = m.id""".format(city, state, country))
			rv = cur.fetchall()

			testReturn = getGenres(rv)
			print (testReturn, file=sys.stderr)

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
						return render_template('search.html', error=error,store=store, advanced1=advanced1, advanced2=advanced2, somedict=somedict, admissions=admissions, revenue=revenue, budget=budget, genres=genres)
				store.append(" - ".join(temp))
			advanced1 = "A map with the returned locations marked will be placed here along with movie recommedations based off of the search query. This is an advanced feature"
                        advanced2 = "Graphical data(such as revenue and ratings) about the movies at the marked locations will be placed here. This is an advanced feature"

		else:
		 	error = "Please choose an option below"
        return render_template('search.html', error=error,store=store, advanced1=advanced1, advanced2=advanced2, somedict=somedict, admissions=admissions, revenue=revenue, budget=budget, genres=genres)

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
