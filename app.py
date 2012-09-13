# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, make_response, render_template, flash, redirect, url_for, session, escape, g, flash
from flask.ext.login import (LoginManager, current_user, login_required,
                            login_user, logout_user, UserMixin, AnonymousUser,
                            confirm_login, fresh_login_required)
from sqlalchemy import Column, Integer, String, create_engine, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import select, and_, or_, not_

DEBUG = True

#connect to the local MySQL Server, Using the debug mode
class User(UserMixin):
  def __init__(self, name, id, is_admin, uid, active=True):
    self.name = name
    self.id = id
    self.active = active
    self.is_admin = is_admin
    self.uid = uid
    
  def is_active(self):
    return self.active



engine = create_engine('mysql://bootstrap:boot@127.0.0.1/dbproj?charset=utf8', echo=True, encoding='utf8' )

Base = declarative_base()
metadata = MetaData(bind = engine)
metadata.reflect()

db_connect = engine.connect()

db_city = Table('city', metadata, autoload=True, autoload_with=engine)
db_admin = Table('admin', metadata, autoload=True, autoload_with=engine)
db_flight_info = Table('flight_info', metadata, autoload=True, autoload_with=engine)
db_flight_seat = Table('flight_seat', metadata, autoload=True, autoload_with=engine)
db_booktable = Table('booktable', metadata, autoload=True, autoload_with=engine)
db_guest = Table('guest', metadata, autoload=True, autoload_with=engine)
db_tickettable = Table('ticket_table', metadata, autoload=True, autoload_with=engine)

lg_userlist = []

def verify_admin(name, password):
  '''Verify the Administrator User from database'''
  s = select([db_admin], and_(db_admin.c.name == name, db_admin.c.password == password))
  result = db_connect.execute(s)
  #Get Database Query Results
  if result.returns_rows == True:
    #Admin Verify OK
    row = result.first()
    ret = User(name = row['name'], id = row['name'], is_admin = True, uid = row['id']);
    if ret not in lg_userlist:
      lg_userlist.append(ret)
    if DEBUG == True:
      print 'Verify OK: Admin:', ret.name
    return ret
  else:
    #Admin Verify Faild. Login incorrect
    result.close()
    return None
    
 
class Anonymous(AnonymousUser):
  name =u"Anonymous"
  
useradmin = User("admin", "testadmin",1,1)

app = Flask(__name__)
app.config.from_pyfile('app.cfg')
login_manager = LoginManager()
login_manager.anonymous_user = Anonymous
login_manager.login_view = "/login/"
login_manager.login_message = "Require Login"

@login_manager.user_loader
def load_user(id):
  '''
  We use username as ID. For the Flask Login Ext require a Unicode ID
  As we log every verified user into lg_userlist. We do not need to
  Access the database here.
  '''
  for item in lg_userlist:
    if item.id == id:
      return item
  return None
   

login_manager.setup_app(app)

## Set SQL Alchemy to automatically tear down
@app.teardown_request
def shutdown_session(exception=None):
    #db_session.remove()
    pass

def load_env():
  if current_user.is_anonymous():
      msg = {'is_admin':False, 'is_login':False, 'username': current_user.name}
  else:
      msg = {'is_admin':current_user.is_admin, 'is_login':True, 'username': current_user.name}
  return msg

def index():
  # if current_user.is_anonymous():
  #   msg = {'is_admin':False, 'is_login':False}
  # else:
  #   msg = {'is_admin':current_user.is_admin, 'is_login':True}
  msg = load_env()
  print msg
  return render_template('index.html',msg = msg)

    
def loaduid(uid):
  '''Load User by UID from database '''
  pass

def verify_user(name, password):
  '''Verify the guest user from database'''
  pass
 
  
##login methods



def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        login_type = request.form['type']
        if DEBUG == True:
	  print "debug: Username = ", username
	  print "debug: Password = ", password
	  print "debug: login_type = ", login_type
	  
	if login_type == 'admin':
	  user = verify_admin(username,password)
	  if user == None:
	    #Login Incorrect
	    flash(u"用户名或密码错误")
	    return render_template('login.html')
	  else:
	    #Login Correct
	    if login_user(user, remember = True):
	      if DEBUG == True:
		print 'Login Successful'
	      return redirect(url_for('home'))  
	  
#	if username == useradmin.name:
#	  if login_user(useradmin, remember = True):
	    #flash("Logged in")
	    #return redirect(url_for('home'))
	  #else:
	    #flash("Login Data Error")
    else:
      return render_template('login.html')
#        user = User.query.filter(User.username==username).first()
#        if user is not None:
            # Authenticate and log in!
#            if user.authenticate(request.form['password']):
#               session['username'] = request.form['username']
#                return redirect(url_for('home'))
#            else:
#                flash('Incorrect password. Please try again')
#                return render_template('login.html')
#        else:
#            flash('Incorrect username. Please try again')
#            return render_template('login.html')
#    return render_template('login.html')

#@login_required()
def home():
    ##Dump variables in templates
    if current_user.is_anonymous():
      return redirect(url_for('login'))
    else:
      msg = {'is_admin':current_user.is_admin, 'is_login':True, 'username': current_user.name}
      return render_template('home.html', msg=msg)

def flight_manage_view():
    ##Dump variables in templates
    if current_user.is_anonymous():
      return redirect(url_for('login'))
    else:
      #Initialize Database Access
      
      msg = {'is_admin':current_user.is_admin, 'is_login':True, 'username': current_user.name}
      return render_template('flight_manage.html', msg=msg)

def user_create():
#    if request.method == 'POST':
#        username = request.form['username']
#        if User.query.filter(User.username==username).first():
#            return 'User already exists.'
#        password = request.form['password']
#        user = User(username=username, password=password)
#        db.session.add(user)
#        db.session.commit()
#        return redirect(url_for('index'))
    return render_template('user_create.html')

def logout_view():
  if DEBUG:
    print current_user.name , current_user.is_anonymous()   
  if current_user.is_anonymous() == False:
    if DEBUG:
      print "Prepare to Logout"
    logout_user()
    msg = {'echotext':u'成功登出' }
    return render_template('logout.html', msg=msg)
  else:
    flash(u"您还未登录")
    return redirect(url_for('index'))
#    user_data = logout()
#    if user_data is None:
#        msg = 'No user to log out.'
#        return render_template('logout.html', msg=msg)
#    else:
#        msg = 'Logged out user {0}.'.format(user_data['username'])
#        return render_template('logout.html', msg=msg)
  
        
def about_view():
  msg = load_env()
  return render_template('about.html', msg = msg)

# URLs
app.add_url_rule('/', 'index', index)
app.add_url_rule('/login/', 'login', login, methods=['GET', 'POST'])
app.add_url_rule('/home/', 'home', home)
app.add_url_rule('/users/create/', 'user_create', user_create, methods=['GET', 'POST'])
app.add_url_rule('/logout/', 'logout', logout_view)
app.add_url_rule('/about/','about' , about_view)
app.add_url_rule('/flight_manage/','flight_manage' , flight_manage_view)

# Secret key needed to use sessions.
app.secret_key = 'mysecretkey'
  
if __name__ == "__main__":
    print "This If code in app.py was executed"
#    try:
#        open('/tmp/app.db')
#    except IOError:
#        db.create_all()
    app.run(debug=True,host='127.0.0.1')
