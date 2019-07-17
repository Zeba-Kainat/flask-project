from flask import Flask,render_template,request,redirect,url_for,session,send_from_directory
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import sha256_crypt
import os
from werkzeug.utils import secure_filename
import re


upload_folder='D:/zeba/python/myrestapi/images'
app = Flask(__name__)

app.config['upload_folder']=upload_folder
app.secret_key = 'meza'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:12345@localhost/api'
db = SQLAlchemy(app)

class accounts(db.Model):
    __tablename__='accounts'
    id = db.Column('id',db.Integer, primary_key=True)
    username = db.Column('username',db.String(80))
    firstname = db.Column('firstname', db.String(200))
    lastname = db.Column('lastname', db.String(200))
    email = db.Column('email',db.String(120))
    password = db.Column('password',db.String(80))
    image=db.Column('image',db.String(500))


@app.route("/", methods=["GET", "POST"])
def login():
    msg=''
    if request.method == "POST" and 'username' in request.form and 'password' in request.form:
        uname = request.form["username"]
        passw = request.form["password"]
        account = accounts.query.filter_by(username=uname).first()



        if sha256_crypt.verify(passw, account.password):
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account.id
            session['username'] = account.username
            session['password'] = account.password
            session['email'] = account.email
            return redirect(url_for('home'))
        else:
            msg = 'Incorrect username/password!'
    return render_template("index.html",msg=msg)


@app.route("/register", methods=["GET", "POST"])
def register():
    msg=''
    if request.method == "POST" and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        uname = request.form['username']
        mail = request.form['email']
        passw =sha256_crypt.encrypt(request.form['password'])

        account=accounts.query.filter_by(username=uname).all()
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', mail):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', uname):
            msg = 'Username must contain only characters and numbers!'
        elif not uname or not passw or not mail:
            msg = 'Please fill out the form!'
        else:
            register = accounts(username=uname, email=mail, password=passw)
            db.session.add(register)
            db.session.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        msg = 'Please fill out the form!'

    return render_template("register.html",msg=msg)

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
    if 'loggedin' in session:
        account=accounts.query.filter_by(id=(session['id'])).first()
        return render_template('profile.html',account=account)
    return redirect(url_for('login'))

@app.route('/updateprofile',methods=['GET','POST'])
def editprofile():
    msg=''
    account=''
    if 'loggedin' in session:
        account = accounts.query.filter_by(id=(session['id'])).first()
        if request.method == 'POST' and 'firstname' in request.form and 'lastname' in request.form:
            firstname = request.form['firstname']
            lastname = request.form['lastname']
            file = request.files['pic']
            if file:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['upload_folder'], filename))
                account = accounts.query.filter_by(id=(session['id'])).first()
                #account = db.session.query(accounts).get(16)

                #db.session.query(accounts).filter_by(id=16).update({"firstname": firstname})
                #db.session.commit()

                account.firstname=firstname
                account.lastname=lastname
                account.image=file.filename

                #account.image=file.filename

                #print(account.lastname)


                db.session.commit()
                msg = 'You have successfully updated your profile!'


    return render_template('editprofile.html',account=account,msg=msg)

@app.route('/upload/<filename>')
def send_image(filename):
    return send_from_directory('D:/zeba/python/myrestapi/images', filename)



if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)