from flask import Flask
from flask_mysqldb import MySQL
from flask import render_template, request, session

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
    return render_template('search.html',store=store)

@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/add', methods=['GET','POST'])
def add_entry():
    db = mysql.connection.cursor()
    db.execute('INSERT INTO Users(email, password, firstName, lastName) values (?, ?, ?, ?)',
                 [request.form['Email'], request.form['Password'], request.form['Fname'], request.form['Lname']])
    db.commit()
    flash('Account created. Please log in')
    return redirect('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['Email'] != app.config['EMAIL']:
            error = 'Invalid email'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('search'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect('index.html')

if __name__ == '__main__':
    app.run(debug=True)
