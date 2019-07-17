from flask import Flask, render_template, request, redirect, url_for, session,send_from_directory
import re
import os
import pymysql.cursors
from passlib.hash import sha256_crypt
from werkzeug.utils import secure_filename


upload_folder='D:/zeba/python/myrestapi/images'


app = Flask(__name__)
app.config['upload_folder']=upload_folder


app.secret_key = 'meza'
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='12345',
                             db='api',
                             cursorclass=pymysql.cursors.DictCursor)

@app.route('/', methods=['GET', 'POST'])
def login():
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']

        password =request.form['password']
        # Check if account exists using MySQL
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM accounts WHERE username = %s',(username))
        # Fetch one record and return result
        account = cursor.fetchone()
            # If account exists in accounts table in out database
        if sha256_crypt.verify(password, account['password']):
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            session['password'] = account['password']
            session['email'] = account['email']
            # Redirect to home page
            return redirect(url_for('home'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('index.html', msg=msg)


@app.route('/register', methods=['GET', 'POST'])
def register():
        msg = ''

        # Check if "username", "password" and "email" POST requests exist (user submitted form)
        if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
            # Create variables for easy access
            username = request.form['username']
            password = sha256_crypt.encrypt(request.form['password'])

            email = request.form['email']

            # Check if account exists using MySQL
            cursor =connection.cursor()
            cursor.execute('SELECT * FROM accounts WHERE username = %s', (username))
            account = cursor.fetchone()

            # If account exists show error and validation checks
            if account:
                msg = 'Account already exists!'
            elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                msg = 'Invalid email address!'
            elif not re.match(r'[A-Za-z0-9]+', username):
                msg = 'Username must contain only characters and numbers!'
            elif not username or not password or not email:
                msg = 'Please fill out the form!'
            else:
                # Account doesnt exists and the form data is valid, now insert new account into accounts table
                cursor.execute('INSERT INTO accounts(id,username,password,email) VALUES (NULL, %s, %s, %s)', (username, password, email))
                connection.commit()
                msg = 'You have successfully registered!'

        elif request.method == 'POST':
            # Form is empty... (no POST data)
            msg = 'Please fill out the form!'
        # Show registration form with message (if any)
        return render_template('register.html', msg=msg)



@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))


@app.route('/home')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/profile')
def profile():
    # Check if user is loggedin
    if 'loggedin' in session:
        # We need all the account info for the user so we can display it on the profile page
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM accounts WHERE id = %s', [session['id']])
        account = cursor.fetchone()
        # Show the profile page with account info
        return render_template('profile.html', account=account)

    # User is not loggedin redirect to login page
    return redirect(url_for('login'))


@app.route('/updateprofile',methods=['GET','POST'])
def editprofile():
    msg=''
    account=''
    if 'loggedin' in session:
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM accounts WHERE id = %s', [session['id']])
        account = cursor.fetchone()
        if request.method == 'POST' and 'firstname' in request.form and 'lastname' in request.form:
            firstname = request.form['firstname']
            lastname = request.form['lastname']
            file = request.files['pic']
            if file:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['upload_folder'], filename))


                cursor = connection.cursor()
                cursor.execute('update accounts set firstname=%s,lastname=%s,image=%s where id=%s',
                               (firstname, lastname, file.filename, [session['id']]))
                connection.commit()
                msg = 'You have successfully updated your profile!'


    return render_template('editprofile.html',account=account,msg=msg)

@app.route('/upload/<filename>')
def send_image(filename):
    return send_from_directory('D:/zeba/python/myrestapi/images', filename)


if __name__ == '__main__':

    app.run(debug=True,
            host='127.1.0.0',
            port=9000,
            threaded=True)