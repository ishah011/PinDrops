import MySQLdb

def locationAnalysis():
    conn = MySQLdb.connect(host='fa16-cs411-29.cs.illinois.edu', user = 'root', passwd = 'cs411fa2016', db = 'imdb')
    rv = []
    db = conn.cursor()

    print ( 'Entering LOCATION ANALYSIS', file=sys.stderr)

    db.execute("""SELECT location FROM Filmed_In WHERE latitude IS NULL""")
    rv = db.fetchall()

    for row in rv:
        location = row[0]
        elements = location.split(",")
        if len(elements) > 2:
            countryCode = elements[-1]
            state = elements[-2]
            city = elements[-3]
            if countryCode is None or state is None or city is None:
                return
            db = conn.cursor()
            db.execute("""SELECT latitude, longitude FROM FilmingLocationAlt WHERE ISO3 = '{}' AND stateName = '{}' AND city = '{}'""".format(countryCode, state, city))
            locRV = db.fetchall()
            if len(locRV) > 0:
                lat = locRV[0][0]
                lng = locRV[0][0]

                print ( 'UPDATING LAT AND LONG WITH VALUES: ' + str(lat) + ' ' + str(lng) + ' FOR ' + str(location), file=sys.stderr)

                db = conn.cursor()
                db.execute("""UPDATE Filmed_In SET latitude = {}, longitude = {} WHERE location = '{}'""".format(lat, lng, location))
                conn.commit()
    conn.close()


locationAnalysis()
