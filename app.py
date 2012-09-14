# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, make_response, render_template, flash, redirect, url_for, session, escape, g, flash
from flask.ext.login import (LoginManager, current_user, login_required,
                            login_user, logout_user, UserMixin, AnonymousUser,
                            confirm_login, fresh_login_required)
from sqlalchemy import Column, Integer, String, create_engine, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import select, and_, or_, not_
from sqlalchemy.exc import IntegrityError

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

class Flight_Infoc(object):
  def __init__(self, id ,fname, ffrom, fto, fset, fdur, farr, fsetday, fprice, fseat):
    self.id = id
    self.fname = fname
    self.ffrom = ffrom
    self.fto = fto
    self.fset = fset
    self.fdur = fdur
    self.farr = farr
    self.fsetday = fsetday
    self.fprice = fprice
    self.fseat = fseat


class Flight_Time(object):
  def __init__(self, minite, hour):
    self.min = minite
    self.hour = hour

  def __repr__(self):
    if self.hour < 10:
      sthour = '0' + str(self.hour)
    else:
      sthour = str(self.hour)

    if self.min < 10:
      sthmin = '0' + str(self.min)
    else:
      sthmin = str(self.min)
    return sthour + ':' + sthmin


class Flight_Day(object):
  def __init__(self, day, month, year):
    self.day = day
    self.month = month
    self.year =year

class Flight_City(object):
  def __init__(self, id, name):
    self.id = id
    self.name = name



def verify_admin(name, password):
  '''Verify the Administrator User from database'''
  s = select([db_admin], and_(db_admin.c.name == name, db_admin.c.password == password))
  result = db_connect.execute(s)
  #Get Database Query Results
  if result.rowcount != 0:
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
    
 
def load_cities():
  '''Load All City Info from database,return a dict`'''
  retdict = {}
  s = select([db_city])
  result = db_connect.execute(s)
  if result.rowcount != 0:
    #The Database contain City data
    row = result.fetchone()
    while row != None:
      cur = Flight_City(row['id'],row['name'])
      retdict[cur.id] = cur
      row = result.fetchone()

    return retdict
  else:
    #The Database contain no City Data
    return retdict

def load_all_flight():
  '''Load all flight info from database, return a list of Flight_Infoc'''
  retlist = []
  #Load All City Info as dict
  citydic = load_cities()
  s = select([db_flight_info])
  result = db_connect.execute(s)
  if result.rowcount != 0:
    #The Database contain Flight Data
    row = result.fetchone()
    while row != None:
      curfrom = citydic[row['cfrom']]
      curto = citydic[row['cto']]
      cursettime = Flight_Time(row['set_min'], row['set_hour'])
      curdurtime = Flight_Time(row['dur_min'], row['dur_hour'])
      arrmin = (cursettime.min + curdurtime.min) % 60
      arrhour = (cursettime.hour + curdurtime.hour) + (cursettime.min + curdurtime.min) / 60
      curarrtime = Flight_Time(arrmin, arrhour)
      curday = Flight_Day(row['set_day'], row['set_mon'], row['set_year'])
      curflight = Flight_Infoc(
        id = row['id'], 
        fname = row['flight'], 
        ffrom = curfrom, 
        fto = curto, 
        fset = cursettime,
        fdur = curdurtime,
        farr = curarrtime,
        fsetday = curday,
        fprice = row['price'],
        fseat = row['remain'])
      retlist.append(curflight)
      row = result.fetchone()
    return retlist
  else:
    #The Database contain no Flight Data
    return retlist

def load_flight_by_name(name):
  '''Load a flight infomation from database by flight name'''
  citydic = load_cities()
  s = select([db_flight_info], and_(db_flight_info.c.flight == name))
  result = db_connect.execute(s)
  if result.rowcount != 0:
    row = result.first()
    curfrom = citydic[row['cfrom']]
    curto = citydic[row['cto']]
    cursettime = Flight_Time(row['set_min'], row['set_hour'])
    curdurtime = Flight_Time(row['dur_min'], row['dur_hour'])
    arrmin = (cursettime.min + curdurtime.min) % 60
    arrhour = (cursettime.hour + curdurtime.hour) + (cursettime.min + curdurtime.min) / 60
    curarrtime = Flight_Time(arrmin, arrhour)
    curday = Flight_Day(row['set_day'], row['set_mon'], row['set_year'])
    curflight = Flight_Infoc(
      id = row['id'], 
      fname = row['flight'], 
      ffrom = curfrom, 
      fto = curto, 
      fset = cursettime,
      fdur = curdurtime,
      farr = curarrtime,
      fsetday = curday,
      fprice = row['price'],
      fseat = row['remain'])
    return curflight
  else:
    return None

def load_flight_by_id(fid):
  '''Load a flight infomation from database by flight name'''
  citydic = load_cities()
  s = select([db_flight_info], and_(db_flight_info.c.id == fid))
  result = db_connect.execute(s)
  if result.rowcount != 0:
    row = result.first()
    curfrom = citydic[row['cfrom']]
    curto = citydic[row['cto']]
    cursettime = Flight_Time(row['set_min'], row['set_hour'])
    curdurtime = Flight_Time(row['dur_min'], row['dur_hour'])
    arrmin = (cursettime.min + curdurtime.min) % 60
    arrhour = (cursettime.hour + curdurtime.hour) + (cursettime.min + curdurtime.min) / 60
    curarrtime = Flight_Time(arrmin, arrhour)
    curday = Flight_Day(row['set_day'], row['set_mon'], row['set_year'])
    curflight = Flight_Infoc(
      id = row['id'], 
      fname = row['flight'], 
      ffrom = curfrom, 
      fto = curto, 
      fset = cursettime,
      fdur = curdurtime,
      farr = curarrtime,
      fsetday = curday,
      fprice = row['price'],
      fseat = row['remain'])
    return curflight
  else:
    return None

def insert_flight_info(insf):
  '''This method will insert a new row in flight_info table in database'''
  if type(insf) != Flight_Infoc:
    return "Insert Info Error"
  citydic = load_cities()
  if (insf.ffrom.id not in citydic) or (insf.fto.id not in citydic):
    return "City Error"
  #skip Flight Name check, leave it to database
  ins = db_flight_info.insert().values(
    flight = insf.fname,
    cfrom  = insf.ffrom.id,
    cto = insf.fto.id,
    set_min = insf.fset.min,
    set_hour = insf.fset.hour,
    set_day = insf.fsetday.day,
    set_mon = insf.fsetday.month,
    set_year = insf.fsetday.year,
    dur_min = insf.fdur.min,
    dur_hour = insf.fdur.hour,
    price = insf.fprice,
    remain = 150)
  try:
    result = db_connect.execute(ins)
  except IntegrityError, e:
    print "Database Access Error: ", e
    return "Insert Data Error"
  else:
    pass
  finally:
    pass
  
  return result

def alter_flight_info(altfs):
  '''Alter A Flight Info By ID'''
  if type(altfs) != Flight_Infoc:
    return "Update Info Error"
  citydic = load_cities()
  if (altfs.ffrom.id not in citydic) or (altfs.fto.id not in citydic):
    return "City Error"
  #skip Flight Name check, leave it to database
  upd = db_flight_info.update().where(db_flight_info.c.id == altfs.id).values(
    id = altfs.id,
    flight = altfs.fname,
    cfrom  = altfs.ffrom.id,
    cto = altfs.fto.id,
    set_min = altfs.fset.min,
    set_hour = altfs.fset.hour,
    set_day = altfs.fsetday.day,
    set_mon = altfs.fsetday.month,
    set_year = altfs.fsetday.year,
    dur_min = altfs.fdur.min,
    dur_hour = altfs.fdur.hour,
    price = altfs.fprice,
    remain = 150)
  try:
    result = db_connect.execute(upd)
  except IntegrityError, e:
    return "Update Data Error"
  else:
    pass
  finally:
    pass
  
  return result

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

    else:
      return render_template('login.html')
       

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
      flightlist = load_all_flight()
      if len(flightlist) == 0:
        #No Flight Data
        msg = {'is_admin':current_user.is_admin, 'is_login':True, 'username': current_user.name, 'flightlist':None}
      else:
        #Flight Data Present
        msg = {
        'is_admin':current_user.is_admin, 'is_login':True, 'username': current_user.name, 'flightlist':flightlist}
      return render_template('flight_manage.html', msg=msg)

def flight_manage_add():
  if current_user.is_anonymous():
    return redirect(url_for('login'))
  else:
    citydic = load_cities()
    if request.method == 'GET':
      # A Get Request
      msg = {'is_admin':current_user.is_admin, 'is_login':True, 'username': current_user.name, 'is_post':False}
      msg['citydic'] = citydic
      return render_template('flight_manage_add.html', msg = msg)
    elif request.method == 'POST':
      #Process Set Time
      msg = {'is_admin':current_user.is_admin, 'is_login':True, 'username': current_user.name, 'is_post':True}
      msg['fset'] = request.form['fset']
      msg['fdur'] = request.form['fdur']
      msg['fname'] = request.form['fname']
      msg['ffrom'] = request.form['ffrom']
      msg['fto'] = request.form['fto']
      msg['fdayday'] = request.form['fdayday']
      msg['fdaymonth'] = request.form['fdaymonth']
      msg['fdayyear'] = request.form['fdayyear']
      msg['fprice'] = request.form['fprice']
      print type(msg['fname'])
      msg['citydic'] = citydic
      try:
        fsetstr = request.form['fset']
        fsetind = fsetstr.index(':')
        fdurstr = request.form['fdur']
        fdurind = fdurstr.index(':')
        fsettime = Flight_Time(int(fsetstr[fsetind+1:len(fsetstr)]), int(fsetstr[0:fsetind]))
        #Process Dur Time
        fdurtime = Flight_Time(int(fdurstr[fdurind+1:len(fdurstr)]), int(fdurstr[0:fdurind]))
        #Process Set Date
        fsetday = int(request.form['fdayday'])
        print "fsetday: ",fsetday
        fsetmon = int(request.form['fdaymonth'])
        print "fsetmon: ",fsetmon
        fsetyear = int(request.form['fdayyear'])
        print "fsetyear: ",fsetyear
        fsetdate = Flight_Day(fsetday, fsetmon, fsetyear)
        fprice = int(request.form['fprice'])
        print "fsetprice: ",fprice
        insfs = Flight_Infoc(
          id = 99,  #Just a Place holder
          fname = request.form['fname'],
          ffrom = citydic[int(request.form['ffrom'])],
          fto = citydic[int(request.form['fto'])],
          fset = fsettime,
          fdur = fdurtime,
          farr = None,
          fsetday = fsetdate,
          fprice = fprice,
          fseat = 180
          )
        result = insert_flight_info(insfs)
        if type(result) != str:
          flash(u"新增航班信息成功")
          return redirect(url_for('flight_manage'))
        else:
          if DEBUG == True:
            print result
          flash(u"航班信息填写有误")
          return render_template('flight_manage_add.html',msg = msg)
      except Exception,e:
        flash(u"航班信息填写有误")
        print e
        return render_template('flight_manage_add.html',msg = msg)
        # flash(u"航班信息填写有误")
        # return render_template('flight_manage_add.html',msg = msg)

    return render_template('flight_manage_add.html', msg = msg)

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
app.add_url_rule('/flight_manage/', 'flight_manage' , flight_manage_view)
app.add_url_rule('/flight_manage_add/', 'flight_manage_add', flight_manage_add, methods=['GET', 'POST'])

# Secret key needed to use sessions.
app.secret_key = 'mysecretkey'
  
if __name__ == "__main__":
    print "This If code in app.py was executed"
#    try:
#        open('/tmp/app.db')
#    except IOError:
#        db.create_all()
    app.run(debug=True,host='127.0.0.1')
