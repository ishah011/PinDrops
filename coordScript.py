import MySQLdb
import sys
import urllib2
import urllib
import json

def locationAnalysis():
    rv = []
    conn = MySQLdb.connect(host='fa16-cs411-29.cs.illinois.edu', user = 'root', passwd = 'cs411fa2016', db = 'imdb')
    db = conn.cursor()

    print 'Entering LOCATION ANALYSIS'

    db.execute("""SELECT location FROM Filmed_In WHERE latitude IS NULL OR latitude = longitude""")
    rv = db.fetchall()

    for row in rv:
        location = row[0]
        elements = location.split(",")
	try:
		location = location.replace("'", "''").encode('ascii', 'ignore')
	except:
		print 'FATAL ERROR IN ENCODING'
		continue
        if len(elements) > 2:
            countryCode = elements[-1].encode('ascii', 'ignore').decode('ascii').strip().replace("'", "")
            state = elements[-2].encode('ascii', 'ignore').decode('ascii').strip().replace("'", "")
            city = elements[-3].encode('ascii', 'ignore').decode('ascii').strip().replace("'","")
            if countryCode is None or state is None or city is None:
                return
	    print countryCode
	    print state
	    print city
            db = conn.cursor()
            db.execute("""SELECT latitude, longitude FROM FilmingLocationAlt WHERE countryName = '{}' AND stateName = '{}' AND city = '{}'""".format(countryCode, state, city))
            locRV = db.fetchall()
            if len(locRV) > 0:
                lat = locRV[0][0]
                lng = locRV[0][1]

                print 'UPDATING LAT AND LONG WITH VALUES: ' + str(lat) + ' ' + str(lng) + ' FOR ' + str(location)

                db = conn.cursor()
                db.execute("""UPDATE Filmed_In SET latitude = {}, longitude = {} WHERE location = '{}'""".format(lat, lng, location))
                conn.commit()
    conn.close()


locationAnalysis()

