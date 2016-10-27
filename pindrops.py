from flask import Flask
from flask_mysqldb import MySQL
from flask import render_template

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
    #return str(",".join(store))+'\n Query: '+to_exec
    return render_template('index.html',store=store)
if __name__ == '__main__':
    app.run(debug=True)
