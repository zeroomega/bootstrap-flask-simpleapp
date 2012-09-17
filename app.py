# -*- coding: utf-8 -*-
from flask import Flask, request, jsonify, make_response, render_template, flash, redirect, url_for, session, escape, g, flash
from flask.ext.login import (LoginManager, current_user, login_required,
                            login_user, logout_user, UserMixin, AnonymousUser,
                            confirm_login, fresh_login_required)
from achemy import *
import base64

DEBUG = True


class Anonymous(AnonymousUser):
  name =u"Anonymous"

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
    msg = {'is_admin':False, 'is_login':False, 'username': current_user.name,'header':''}
  else:
    msg = {'is_admin':current_user.is_admin, 'is_login':True, 'username': current_user.name, 'uid': current_user.id,'header':''}
  return msg

def index():
  # if current_user.is_anonymous():
  #   msg = {'is_admin':False, 'is_login':False}
  # else:
  #   msg = {'is_admin':current_user.is_admin, 'is_login':True}
  msg = load_env()
  msg['header'] = 'home'
  print msg
  return render_template('index.html',msg = msg)
  
##login methods



def login():
  '''Login Page'''
  msg = load_env()
  msg['header'] = 'login'
  if request.method == "POST":
    username = request.form['username']
    password = request.form['password']
    login_type = request.form['type']
    
    if login_type == 'admin':
      user = verify_admin(username,password)      
      if user == None:
        #Login Incorrect
        flash(u"用户名或密码错误")
        return render_template('login.html', msg = msg)
      else:
        #Login Correct
        if login_user(user, remember = True):
          if DEBUG == True:
            print 'Login Successful'
        return redirect(url_for('home'))
    if login_type == 'guest':
      user = verify_guest(username, password)
      if user == None:
        #Login Incorrect
        flash(u"用户名或密码错误")
        return render_template('login.html', msg = msg)
      else:
        #Login Correct
        if login_user(user, remember = True):
          if DEBUG == True:
            print 'Login Successful'
        return redirect(url_for('home'))

  if request.method == "GET":
    return render_template('login.html', msg = msg)
       

#@login_required()
def home():
    ##Dump variables in templates
    if current_user.is_anonymous():
      return redirect(url_for('login'))
    else:
      msg = {'is_admin':current_user.is_admin, 'is_login':True, 'username': current_user.name}
      msg['header']='home'
      return render_template('home.html', msg=msg)

def flight_manage_view():
    ##Dump variables in templates
    if current_user.is_anonymous():
      return redirect(url_for('login'))
    else:
      #Initialize Database Access
      flightlist = load_all_flight()
      guestdict = load_all_guests()
      if len(flightlist) == 0:
        #No Flight Data
        msg = {'is_admin':current_user.is_admin, 'is_login':True, 'username': current_user.name, 'flightlist':None, 
        'guestdict':guestdict}
      else:
        #Flight Data Present
        msg = {
        'is_admin':current_user.is_admin, 'is_login':True, 'username': current_user.name, 'flightlist':flightlist,
        'guestdict':guestdict}
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
      msg['frow'] = request.form['frow']
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
        
        fsetmon = int(request.form['fdaymonth'])
        
        fsetyear = int(request.form['fdayyear'])
        
        fsetdate = Flight_Day(fsetday, fsetmon, fsetyear)
        fprice = int(request.form['fprice'])
        frow = int(request.form['frow'])
        fseat = frow * 9
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
          fseat = fseat
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

def flight_manage_del():
  '''Flight Info Delete Handler'''
  if current_user.is_anonymous():
    return redirect(url_for('login'))
  else:
    if DEBUG == True:
      print "delete debug"
    fid = int(request.args['id'])    
    ret = delete_flight_id(fid)
    if ret != None:
      flash(u"删除成功")
      return redirect(url_for('flight_manage'))
    else:
      flash(u"删除失败")
      return redirect(url_for('flight_manage'))

def book_ticket_view():
  '''Let the Admin select a guest'''
  if current_user.is_anonymous():
    return redirect(url_for('login'))
  if request.method == 'GET':
    return redirect(url_for_('home'))
  #Process Postdata

  fid = int(request.form['hfid'])
  gid = int(request.form['hgid'])
  if DEBUG == True:
    print "POST DATA fid", fid,"gid",gid
  if count_ticket_remain(fid) == 0:
    flash(u"票已经售完")
    return redirect(url_for('flight_manage'))

  #Book a ticket
  bid = book_a_flight(gid,fid)
  if DEBUG == True:
      print "Ticket Booked, bid",bid
  if bid == None:
    flash(u"订票时出现未知错误，请联系管理员")
    return redirect(url_for('flight_manage'))

  flash(u"订票成功")
  binfo = load_book_by_id(int(bid))
  if binfo == None:
    print "Critical Error in book_ticket_view2"
    return redirect(url_for('flight_manage'))

  msg = load_env()
  srow = binfo.pos / 9
  scol = binfo.pos % 9
  msg['srow'] = srow
  finfoc = load_flight_by_id(fid)
  reminddate = finfoc.fsetday
  reminddate.prior()
  msg['scol'] = scol
  msg['ticket'] = base64.b64encode(str(binfo.tid + 5))
  msg['remind'] = base64.b64encode(str(binfo.rid))
  msg['reminddate'] = reminddate
  msg['money'] = finfoc.fprice
  return render_template("remind.html",msg = msg)

def ticket_info_view():
  '''This method display the ticket info of the user'''
  if request.method == "GET":
    bid = request.args['bid']
  if request.method == "POST":
    bid = request.form['bid']
  binfo = load_book_by_id(int(bid))
  if binfo == None:
    print "Critical Error in ticket_info_view"
    return redirect(url_for('flight_manage'))
  msg = load_env()
  srow = binfo.pos / 9
  scol = binfo.pos % 9
  msg['srow'] = srow
  finfoc = binfo.finfoc
  reminddate = finfoc.fsetday
  reminddate.prior()
  msg['scol'] = scol
  #IS Paid
  msg['ticket'] = base64.b64encode(str(binfo.tid + 5))
  #IS Get
  msg['remind'] = base64.b64encode(str(binfo.rid))
  msg['reminddate'] = reminddate
  msg['money'] = finfoc.fprice
  return render_template("remind.html",msg = msg)

def flight_info_view():
  '''Display details of a flight'''
  if current_user.is_anonymous():
    return redirect(url_for('login'))
  if request.method == 'GET':
    fid = int(request.args['fid'])
  if request.method == 'POST':
    fid = int(request.form['fid'])
  msg = load_env()  
  finfoc = load_flight_by_id(fid)
  ticket_remain = count_ticket_remain(fid)
  fullrate =1 - float(ticket_remain) / float(finfoc.fseat) 
  fullrate = fullrate * 100
  rawstr = str(fullrate)
  rawstr = rawstr[0:rawstr.index('.')+2] + '%'
  msg['finfoc'] = finfoc
  msg['ticket_remain'] = ticket_remain
  msg['fullrate'] = rawstr
  tdict = load_book_items_by_fid(fid)
  msg['tdict'] =tdict
  return render_template("view_flight.html",msg = msg)

def book_revoke_view():
  '''This method revoke a book action in book table'''
  if request.method == 'GET':
    bid = request.args['bid']
  if request.method == 'POST':
    bid = request.form['bid']
  ret = delete_a_book(int(bid))
  if ret == 1:
    flash(u"退订成功")
    return redirect(request.referrer)
  print ret
  return redirect(request.referrer)

def get_ticket_view():
  '''Display Get A Ticket '''
  if current_user.is_anonymous():
    return redirect(url_for('login'))
  msg = load_env()
  return render_template("get_ticket.html", msg = msg)

def get_ticket_action():
  '''Get A Ticket by tid & bid'''
  if current_user.is_anonymous():
    return redirect(url_for('login'))
  msg = load_env()
  if request.method == "GET":
    return render_template('view_ticket.html', msg = msg)
  if request.method == "POST":
    b64tid = request.form['tid']
    b64rid= request.form['rid']
    tid = int(base64.b64decode(b64tid)) - 5
    rid = int(base64.b64decode(b64rid))
    bookinfoc = load_book_by_tid_rid(tid,rid)
    if bookinfoc == None:
      flash(u"您输入的信息有误，请重试")
      return render_template("get_ticket.html", msg = msg)
    #Get the bookinfoc
    if (bookinfoc.isget == 1) or (bookinfoc.ispay == 1):
      flash(u"您已经取票过了")
    else:
      flash(u"取票成功")
    pay_a_ticket(tid)
    revoke_a_remind(rid)
    msg['bookinfoc'] = bookinfoc
    code = base64.b64encode(str(bookinfoc.id))
    msg['code'] = code
    return render_template("view_ticket.html", msg = msg)

def sell_ticket_view():
  '''This method help a user choose a flight and book a ticket'''
  if current_user.is_anonymous():
    return redirect(url_for('login'))
  msg = load_env()
  citydic = load_cities()
  msg['citydic'] = citydic
  guestdic = load_all_guests()
  msg['guestdic'] = guestdic
    
  if request.method == 'GET':
    flightdic = load_all_flight()
    msg['flightlist'] = flightdic
    msg['effrom'] = 65535
    msg['efto'] = 65535
    msg['eid'] = 1
    return render_template('sell_ticket.html',msg = msg)
  if request.method == 'POST':
    gid = int(request.form['gid'])
    effrom = int(request.form['ffrom'])
    efto = int(request.form['fto'])
    if effrom == 65535:
      ffrom = None
    else:
      ffrom = effrom
    if efto == 65535:
      fto = None
    else:
      fto = efto
    flightdic = query_flight_id(ffrom = ffrom, fto = fto)
    msg['flightlist'] = flightdic
    msg['effrom'] = effrom
    msg['efto'] = efto
    msg['eid'] = gid

  return render_template('sell_ticket.html',msg = msg)


def user_create():
  msg = load_env()
  msg['username'] = ""
  msg['email'] = ""
  if request.method == 'GET':
    return render_template('user_create.html', msg = msg)
  if request.method == 'POST':
    username = request.form['username']
    password = request.form['password']
    password2 = request.form['password2']
    email = request.form['email']
    msg['username'] = username
    msg['email'] = email
    if password2 != password:
      flash(u"两次密码不一致")
      return render_template('user_create.html', msg = msg)
    #proceed Insert
    ret = add_guest(
      username = username,
      password = password,
      email = email)
    if ret == None:
      flash(u"用户名重复")
      return render_template('user_create.html', msg = msg)
    flash(u"注册成功")
    logout_user()
    user = verify_guest(username, password)
    login_user(user,remember = True)

    return redirect(url_for('home'))
    return render_template('user_create.html', msg = msg)


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
  msg['header']='about'
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
app.add_url_rule('/flight_manage_delete', 'flight_manage_delete', flight_manage_del, methods=['GET', 'POST'])
app.add_url_rule('/book_ticket_view', 'book_ticket_view', book_ticket_view, methods=['GET', 'POST'])
app.add_url_rule('/flight_info','flight_info',flight_info_view, methods=['GET', 'POST'])
app.add_url_rule('/book_revoke_view','book_revoke_view',book_revoke_view, methods=['GET', 'POST'])
app.add_url_rule('/ticket_info_view','ticket_info_view',ticket_info_view, methods=['GET', 'POST'])
app.add_url_rule('/get_ticket_view','get_ticket_view',get_ticket_view, methods=['GET', 'POST'])
app.add_url_rule('/get_ticket_action','get_ticket_action',get_ticket_action, methods=['GET', 'POST'])
app.add_url_rule('/sell_ticket_view','sell_ticket_view',sell_ticket_view, methods=['GET', 'POST'])


# Secret key needed to use sessions.
app.secret_key = 'mysecretkey'
  
if __name__ == "__main__":
    print "This If code in app.py was executed"
#    try:
#        open('/tmp/app.db')
#    except IOError:
#        db.create_all()
    app.run(debug=True,host='127.0.0.1')
