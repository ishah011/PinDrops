from __future__ import print_function
from flask import Flask
from flask_mysqldb import MySQL
from flask import render_template, request, session, flash, redirect, url_for, json, jsonify
from flask_debugtoolbar import DebugToolbarExtension 

from operator import itemgetter
import sys
import urllib2
import urllib
import json
import googlemaps
import plotly.plotly as py
import plotly.graph_objs as go
import plotly
import plotly.tools as tls

#plotly.tools.set_credentials_file(username='PinDroppers2', api_key='PoFsPCy53sTLI4U7gKLT')
#plotly.tools.set_credentials_file(username='sloznjakovic', api_key='tv1QymjN1eHQgH68ywin')
plotly.tools.set_credentials_file(username='icanstdssfsdd', api_key='I0tHpMLP8rxiQurUC6YZ')
#plotly.tools.set_credentials_file(username='jack00101', api_key='ld3yHVcfmzWKhdzdK1Gd')
#plotly.tools.set_credentials_file(username='thesecond0001', api_key='3i8LkHXAeQ529aib9l3e')
#plotly.tools.set_credentials_file(username='ineedthis001', api_key='4WRIfGDhhxHNdOPcinMT')


app = Flask(__name__)

#app.debug = True
#app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


mysql = MySQL(app)
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'cs411fa2016'
app.config['MYSQL_DB'] = 'imdb'
app.config['MYSQL_HOST'] = 'fa16-cs411-29.cs.illinois.edu'
app.secret_key = """p6\x9e\x08B\xe2\x11/\xbd\xd6k\xb7=\xc3\xd6p\x96\x90S\xd4z\x8f\xe2\r"""

somedict = None

users = ['jack00101', 'thesecond0001', 'ineedthis001'] 
keys = ['ld3yHVcfmzWKhdzdK1Gd', '3i8LkHXAeQ529aib9l3e', '4WRIfGDhhxHNdOPcinMT']


def recomendationFromLocation(lat, long):
	from sets import Set
	ret = Set([])
	conn = mysql.connection
	
	db = conn.cursor()
	db.execute("""select title, Cast(movie_info.info as decimal),
	( 3959 * acos( cos( radians({}) )* cos( radians( Filmed_In.latitude ) ) * cos( radians( Filmed_In.longitude ) - radians({}) )+ sin( radians({}) ) * sin( radians( Filmed_In.latitude ) ) ) ) AS distance
	from Filmed_In, movie_info, Movies 
	where Filmed_In.latitude between {} and {} 
	and Filmed_In.longitude between {} and {} 
	and Movies.id = Filmed_In.movie_id
	and movie_info.movie_id = Filmed_In.movie_id 
	and movie_info.info_type_id = 101 
	having distance < 10 
	order by movie_info.info desc
	LIMIT 50;""".format(lat, long, lat, lat-2, lat+2, long-2, long+2))
	result = db.fetchall()
	
	if len(result) > 0:
		for rtRev in result:
			ret.add(rtRev[0])
			
			if len(ret) == 10:
				break
	
	return list(ret)

	
def recomendationFromMovie(movie_id):
	from sets import Set
	ret = Set([])
	conn = mysql.connection
	
	db = conn.cursor()
	db.execute("""SELECT AVG(latitude)
FROM Filmed_In
where Filmed_In.movie_id = {};""".format(movie_id))

	avgLat = db.fetchone()

	db.execute("""SELECT AVG(longitude)
FROM Filmed_In
where Filmed_In.movie_id = {};""".format(movie_id))

	avgLong = db.fetchone()

	if avgLong[0] is None or avgLat[0] is None:
		ret.add("No suggestions")
		return list(ret)

	db.execute("""SELECT latitude, longitude
FROM Filmed_In
where Filmed_In.movie_id = {}
and latitude is not NULL
order by (POWER({}-Filmed_In.latitude, 2) + POWER({}-Filmed_In.longitude, 2))
limit 1;""".format(movie_id, avgLat[0], avgLong[0]))

	actual = db.fetchone()


	db.execute("""select title, Cast(movie_info.info as decimal),
       ( 3959 * acos( cos( radians({}) ) 
              * cos( radians( Filmed_In.latitude ) ) 
              * cos( radians( Filmed_In.longitude ) - radians({}) ) 
              + sin( radians({}) ) 
              * sin( radians( Filmed_In.latitude ) ) ) ) AS distance 
from Filmed_In, movie_info, Movies
where Filmed_In.latitude between {}-2 and {}+2 
and Filmed_In.longitude between {}-2 and {}+2
and Movies.id = Filmed_In.movie_id
and Movies.id <> {}
and movie_info.movie_id = Filmed_In.movie_id
and movie_info.info_type_id = 101
having distance < 10
order by movie_info.info desc
LIMIT 50;""".format(actual[0], actual[1], actual[0], actual[0], actual[0], actual[1], actual[1], movie_id))

	result = db.fetchall()
	
	if len(result) > 0:
        	for rtRev in result:
			ret.add(rtRev[0])
			
			if len(ret) == 10:
				break
	
	return list(ret)

def recomendationFromActor(personId):
    ret = []
    conn = mysql.connection
	
    db = conn.cursor()
	
    db.execute("""SELECT title From ActedIn ai, Movies m where ai.person_id = {} and ai.movie_id = m.id;""".format(personId))
	
    result = db.fetchall()
    
    if len(result) > 0:
        for rtRev in result:
			ret.append(rtRev[0])
			
			if len(ret) == 10:
				break


    return ret



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
		rev = [int(s) for s in rev.split(" ") if s.isdigit()]

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
		rev = [int(s) for s in rev.split(" ") if s.isdigit()]

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
		rev = [int(s) for s in rev.split(" ") if s.isdigit()]

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
    if searchString is None:
	return
    try:
    	APIurl = "https://maps.googleapis.com/maps/api/geocode/json?address={}&key=AIzaSyCaGXqswUJlWF3x9IpdEG2DdA-UhUqaAN0".format(urllib.quote_plus(searchString))
    	content = urllib2.urlopen(APIurl).read()
    except:
	print ('SEVER RETURNED EXCEPTION!!!', file=sys.stderr)
	return
    json_data = json.loads(content)


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


def getGraphs(rv, values):
	#ADMISSIONS
	dat1 = getAdmissions(rv)
	data = [go.Bar(
			x= dat1[0],
   			y= dat1[1],
			hoverinfo = "skip"
		)]
	layout = go.Layout(
	    title='Admissions',
	)
	fig = go.Figure(data=data, layout=layout)
	try:
		values[0] = tls.get_embed(py.plot(fig, filename='admissions', fileopt = 'overwrite'))
	except:
		print ('API LIMIT REACHED', file=sys.stderr)
	
	#REVENUE
	dat2 = getRevenue(rv)
	data = [go.Bar(
		x= dat2[0],
		y= dat2[1],
		hoverinfo = "skip"
	)]
	layout = go.Layout(
	    title='Revenue',
	)
	fig = go.Figure(data=data, layout=layout)
	try:
		values[1] = tls.get_embed(py.plot(fig, filename='revenue', fileopt = 'overwrite'))
	except:
		print ('API LIMIT REACHED', file=sys.stderr)

	#BUDGETS
	dat3 = getBudgets(rv)
	data = [go.Bar(
			x= dat3[0],
   			y= dat3[1],
			hoverinfo = "skip"
		)]
	layout = go.Layout(
	    title='Budgets',
	)
	fig = go.Figure(data=data, layout=layout)
	try:
		values[2] = tls.get_embed(py.plot(fig, filename='budget', fileopt='overwrite'))
	except:
		print ('API LIMIT REACHED', file=sys.stderr)

	#GENRES
	dat4 = getGenres(rv)
	fig = {
		'data': [{'labels': dat4[0],
    		'values': dat4[1],
    		'type': 'pie'}],
		'layout': {'title': 'Genres filmed'}
	}
	try:
		values[3] = tls.get_embed(py.plot(fig, filename='genres', fileopt='overwrite'))
	except:
		print ('API LIMIT REACHED')

	return values

@app.route('/')
def index(store=None):
    return render_template('search.html')

@app.route('/search', methods=['GET','POST'])
def search():
	global somedict
	error = None
	store = []
	advanced1 = ""
	advanced2 = ""
	#somedict = {}
	recommend = ""
	admissions = ""
	revenue = ""
	budget = ""
	genres = ""
	new_vals = ["","","",""]
	if request.method == 'POST':
		cur = mysql.connection.cursor()
		if request.form['selection'] == 'Actor':


			fname = request.form['firstName']
			fname = fname.capitalize()
			lname = request.form['lastName']
			lname = lname.capitalize()

			cur.execute("""SELECT a.person_id FROM Actors t, ActedIn a WHERE t.name='{}, {}' AND t.actor_id = a.person_id""".format(lname, fname))
			rv = cur.fetchone()
			if rv is not None: 
				recommend = recomendationFromActor(rv[0])

			cur.execute("""SELECT m.id, m.title, f.location, f.latitude, f.longitude FROM imdb.Movies m LEFT JOIN imdb.Filmed_In f ON f.movie_id = m.id LEFT JOIN imdb.ActedIn a ON a.movie_id = m.id LEFT JOIN imdb.Actors t ON t.actor_id = a.person_id WHERE t.name = '{}, {}'""".format(lname, fname))
			rv = cur.fetchall()

			#print (rv, file=sys.stderr)

			name = []
			xcoord = []
			ycoord = []
			for i in rv:
				mID = i[0]
				mTitle = i[1]
				mLocation = i[2]
				mLat = i[3]
				mLng = i[4]

				if mLat is None:
					continue
				try:
					tag = str(mTitle.decode('iso-8859-1').encode('ascii','ignore')) + " - " + str(mLocation.decode('iso-8859-1').encode('ascii','ignore'))
				except:
					continue
				name.append(tag)
				xcoord.append(mLat)
				ycoord.append(mLng)

			store = name
			
			#JSON FOR GOOGLE MAPS MARKERS
			somedict={		"name"		:	[i for i in name],
						"xcoord"	:	[x for x in xcoord],
						"ycoord"	:	[y for y in ycoord]
			}
			#with open('static/markers.txt', 'w') as outfile:
			#	json.dump(somedict, outfile)
			#GET GRAPHS
			values = [admissions, revenue, budget, genres]
			new_vals = getGraphs(rv, values)



			advanced1 = "A map with the returned locations marked will be placed here along with movie recommedations based off of the search query. This is an advanced feature"
		elif request.form['selection'] == 'Movie':
		 	movieName = request.form['movieName']
			movieName = movieName.capitalize()

			cur.execute("""SELECT DISTINCT m.id FROM Movies m WHERE m.title LIKE'%{}%'""".format(movieName))
			rv = cur.fetchone()
			if rv is not None:
				recommend = recomendationFromMovie(rv[0])

			cur.execute("""SELECT DISTINCT m.id, m.title, f.location, f.latitude, f.longitude FROM Filmed_In f, Movies m WHERE m.title LIKE'%{}%' AND f.movie_id = m.id""".format(movieName))
			rv = cur.fetchall()
			
			
   			name = []
			xcoord = []
			ycoord = []
			for i in rv:
				mID = i[0]
				mTitle = i[1]
				mLocation = i[2]
				mLat = i[3]
				mLng = i[4]

				if mLat is None:
					continue

				try:
					tag = str(mTitle.decode('iso-8859-1').encode('ascii', 'ignore')) + " - " + str(mLocation.decode('iso-8859-1').encode('ascii', 'ignore'))
				except:
					continue
				name.append(tag)
				xcoord.append(mLat)
				ycoord.append(mLng)

			store = name
			
			#JSON FOR GOOGLE MAPS MARKERS
			somedict={		"name"		:	[i for i in name],
						"xcoord"	:	[x for x in xcoord],
						"ycoord"	:	[y for y in ycoord]
			}
			with open('static/markers.txt', 'w') as outfile:
				json.dump(somedict, outfile)
			#GET GRAPHS
			values = [admissions, revenue, budget, genres]
			new_vals = getGraphs(rv, values)

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
			
			cur.execute("""SELECT f.latitude, f.longitude FROM Filmed_In f WHERE f.location = '{}, {}, {}'""".format(city, state, country))
			rv = cur.fetchone()
			if rv is not None:
				recommend = recomendationFromLocation(float(rv[0]), float(rv[1]))

			cur.execute("""SELECT m.id, m.title, f.location, f.latitude, f.longitude FROM imdb.Filmed_In f, imdb.Movies m WHERE f.location = "{}, {}, {}" AND f.movie_id = m.id""".format(city, state, country))
			rv = cur.fetchall()


   			name = []
			xcoord = []
			ycoord = []
			for i in rv:
				mID = i[0]
				mTitle = i[1]
				mLocation = i[2]
				mLat = i[3]
				mLng = i[4]

				if mLat is None:
					continue

				try:
					tag = str(mTitle.decode('iso-8859-1').encode('ascii', 'ignore')) + " - " + str(mLocation.decode('iso-8859-1').encode('ascii', 'ignore'))
				except:
					continue
				name.append(tag)
				xcoord.append(mLat)
				ycoord.append(mLng)

			store = name
			
			#JSON FOR GOOGLE MAPS MARKERS
			somedict={		"name"		:	[i for i in name],
						"xcoord"	:	[x for x in xcoord],
						"ycoord"	:	[y for y in ycoord]
			}
			with open('static/markers.txt', 'w') as outfile:
				json.dump(somedict, outfile)
			#GET GRAPHS
			values = [admissions, revenue, budget, genres]
			new_vals = getGraphs(rv, values)

		else:
		 	error = "Please choose an option below"
        return render_template('search.html', error=error,store=store, somedict=somedict, admissions=new_vals[0], revenue=new_vals[1], budget=new_vals[2], genres=new_vals[3], recommend=recommend)


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
        	session['username'] = email
		session['logged_in'] = True
		list(rv)
		store = []
		for i in rv:
			store.append(str(i))
		result = ",".join(store)
		return redirect(url_for('search'))

    return render_template('login.html', error=error, loggedin=loggedin, result=result)

@app.route('/markers')
def markers():
	return jsonify(**somedict)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('search'))

@app.route('/delete')
def delete():
	email = session['username']
	conn = mysql.connection
	db = conn.cursor()
	db.execute("""DELETE FROM Users WHERE email='{}'""".format(email))
	conn.commit()
	session.pop('logged_in', None)
	session.pop('username', None)
	return redirect(url_for('search'))

@app.route('/update',methods=['GET', 'POST'])
def update():
	message = ""
	if request.method == 'POST':
		email = session['username']
		Npassword = request.form['Npassword']
		Opassword = request.form['Opassword']
		conn = mysql.connection
		db = conn.cursor()
		db.execute("""SELECT * FROM Users WHERE email='{}' AND password='{}'""".format(email, Opassword))
		rv = db.fetchone()
		if rv is not None:
			db.execute("""UPDATE Users SET password = '{}' WHERE email='{}'""".format(Npassword, email))
			conn.commit()
			message = "Password has been updated"
		else:
			message = "Invalid email/password"

	return render_template('update.html', message=message)
if __name__ == '__main__':
    app.run(debug=True)
