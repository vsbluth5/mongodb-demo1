# ---- YOUR APP STARTS HERE ----
# -- Import section --
from flask import Flask
from flask import render_template, request, redirect, session, url_for
from flask_pymongo import PyMongo
import os

## to use ObjectId
from bson.objectid import ObjectId

# -- Initialization section --
app = Flask(__name__)

# THE SESSION INFO
# This creates a session in Python 3
app.secret_key = '_5#y2L"F4Q8z\n\xec]/'

# Get my variables from my .env
app.config['MONGO_DBNAME'] = os.getenv('DBNAME')
app.config['USER'] = os.getenv('DBUSER')
app.config['MONGO_PWD'] = os.getenv('DBPWD')

DBNAME= app.config['MONGO_DBNAME']
DBUSER = app.config['USER']
DBPWD = app.config['MONGO_PWD']

# URI of database
# app.config['MONGO_URI'] = os.getenv('MONGO_URI') # won't work
app.config['MONGO_URI'] = f"mongodb+srv://{DBUSER}:{DBPWD}@cluster0.vmzkd.mongodb.net/{DBNAME}?retryWrites=true&w=majority"


mongo = PyMongo(app)

# -- Routes section --
# LOGIN (where we start)

@app.route('/')
@app.route('/login', methods = ['GET', 'POST'])
def show_login():
    if request.method =='GET':
        return render_template('login.html')
    else:
        users = mongo.db.users
        login_user = users.find_one({'name' : request.form['username']})
        
        if login_user:
            if request.form['password'] == login_user['password']:
                session['username'] = request.form['username']
                return redirect(url_for('index'))
            else:
                return redirect(url_for('show_signup'))

@app.route('/signup', methods = ['GET', 'POST'])
def show_signup():
    if request.method =='GET':
        return render_template('signup.html')
    else:
        users = mongo.db.users
        existing_user = users.find_one({'name' : request.form['username']})

        if existing_user is None:
            users.insert({'name' : request.form['username'], 'password' : request.form['password']})
            session['username'] = request.form['username']
            return redirect(url_for('index'))
        else:
            return redirect (url_for('show_login'))


## Log out
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# Display community board 
@app.route('/index')
def index():
    # get the collection you want to use
    collection = mongo.db.events

    #Use the find method to get all the data from the collection
    events = collection.find({})
    return render_template('index.html', events=events)

# DISPLAY THE FORM
@app.route('/displayform')
def display_form():
    return render_template('form.html')


# CONNECT TO DB, ADD DATA
@app.route('/events/new', methods=['GET', 'POST'])

def new_event():
    if request.method == "GET":
        return redirect('/')
    else:
        if session['username']:
            print(request.form)
            event_name = request.form['event_name']
            event_date = request.form['event_date']

            collection = mongo.db.events
            collection.insert({'event': event_name, 'date': event_date, 'user': session['username']})
            return redirect('/index')
        else:
          return redirect('/')  

## Show the events sorted by date
@app.route('/sortevents')
def sort_events():
    collection = mongo.db.events
    events = collection.find({}).sort('date', -1)
    return render_template('index.html', events=events)

# Delete one using id
@app.route('/remove/<event_id>')
def remove_event(event_id):
    collection = mongo.db.events
    collection.delete_one({'_id': ObjectId(event_id)})
    return redirect('/')