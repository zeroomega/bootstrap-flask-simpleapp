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
from random import randint

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
    if minite < 60:
      self.min = minite
    else:
      self.min = minite % 60

    if minite / 60 > 0:
      self.hour = hour + minite / 60
    else:
      self.hour = hour
    self.hour = self.hour % 24


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

class Flight_Guest(object):
  def __init__(self, id, name, email):
    self.id = id
    self.name = name
    self.email = email

  def __repr__(self):
    return self.name

class Flight_Book_Item(object):
  def __init__(self, id, gid, fid, sid, tid, rid, pos,ispay, isget):
    self.id = id
    self.gid = gid
    self.fid = fid
    self.sid = sid
    self.tid = tid
    self.rid = rid
    self.pos = pos
    self.ispay = ispay
    self.isget = isget


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
db_remindtable = Table('remind_table', metadata, autoload=True, autoload_with=engine)

lg_userlist = []

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
      arrhour = arrhour % 24
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
        fseat = row['seat'])
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
      fseat = row['seat'])
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
      fseat = row['seat'])
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
    seat = insf.fseat)
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
    seat = altfs.fseat)
  try:
    result = db_connect.execute(upd)
  except IntegrityError, e:
    return "Update Data Error"
  else:
    pass
  finally:
    pass
  
  return result



def delete_flight_id(fid):
  '''This method delete a flight_info row by the id'''
  if type(fid) != int:
    return None
  fdel = db_flight_info.delete().where(db_flight_info.c.id == fid)
  ret = db_connect.execute(fdel)
  return ret

def count_ticket(fid):
  '''This method count remain ticket in the flight_seat table'''
  if type(fid) != int:
    return None
  s = select([db_flight_seat], and_(db_flight_seat.c.fid == fid))
  result = db_connect.execute(s)
  count  = result.rowcount
  result.close()
  return count

def count_ticket_remain(fid):
  '''This method count remain ticket in the flight_seat table'''
  if type(fid) != int:
    return None
  s = select([db_flight_seat], and_(db_flight_seat.c.fid == fid))
  result = db_connect.execute(s)
  count = result.rowcount
  result.close()
  infoc = load_flight_by_id(fid)
  return infoc.fseat - count

def list_seat_not_avail(fid):
  '''This method return a list of not available seats'''
  if type(fid) != int:
    return None
  s = select([db_flight_seat], and_(db_flight_seat.c.fid == fid))
  result = db_connect.execute(s)
  if result.rowcount == 0:
    result.close()
    return []
  retlist = []
  row = result.fetchone()
  while row != None:
    retlist.append(int(row['pos']))
    row = result.fetchone()
  return retlist

def choose_a_seat(fid):
  '''This method return an available seat'''
  nalist = list_seat_not_avail(fid)
  infoc = load_flight_by_id(fid)
  avlist = []

  i = 1
  while i <= infoc.fseat:
    if i not in nalist:
      avlist.append(i)
    i = i + 1
  pos = randint(1,len(avlist))
  print "avail list:", len(avlist)
  return avlist[pos-1]


def book_a_seat(fid):
  '''This method try to book a seat, return a dict'''
  ret = count_ticket_remain(fid)
  if (ret == None) or (ret == 0):
    return None
  avpos = choose_a_seat(fid)
  ins = db_flight_seat.insert().values(fid = fid, pos = avpos)
  try:
    result = db_connect.execute(ins)
  except Exception, e:
    print "Error while book a seat", e
    return None
  sid = int(result.inserted_primary_key[0])
  dict = {'sid':sid, 'fid':fid, 'pos':avpos}
  result.close()
  return dict

def revoke_a_seat(sid):
  '''This method try to revoke a seat from seat table'''
  if DEBUG == True:
    print "Try to delete a seat at id ",sid    
  delop = db_flight_seat.delete().where(db_flight_seat.c.id == sid)
  try:
    result = db_connect.execute(delop)
  except Exception, e:
    print "Error while revoke a seat: ", e
    return None
  result.close()
  return 1


def generate_a_ticket():
  '''Generate a unpaid ticket, return the tid'''
  ins = db_tickettable.insert().values(ispay = 0)
  try:
    result = db_connect.execute(ins)
  except Exception, e:
    print "Error while generate_a_ticket", e
    return None
  tid = int(result.inserted_primary_key[0])
  return tid

def pay_a_ticket(tid):
  if type(tid) != int:
    return None
  alt = db_tickettable.update().where(db_tickettable.c.id == tid).values(ispay = 1)
  try:
    result = db_connect.execute(alt)
  except Exception, e:
    print "Error while Pay a ticket", e
    return None
  return 1

def delete_a_ticket(tid):
  if type(tid) != int:
    return None
  delop = db_tickettable.delete().where(db_tickettable.c.id == tid)
  try:
    result = db_connect.execute(delop)
  except Exception, e:
    print "Error while delete a ticket", e
    return None
  return 1

def generate_a_remind():
  '''Generate A remind in remind_table'''
  ins = db_remindtable.insert().values(isget = 0)
  try:
    result = db_connect.execute(ins)
  except Exception, e:
    print "Error while generate_a_remind", e
    return None
  rid = int(result.inserted_primary_key[0])
  return rid

def revoke_a_remind(rid):
  '''Revoke a remind from remind_table'''
  if type(rid) != int:
    return None
  alt = db_remindtable.update().where(db_tickettable.c.id == rid).values(isget = 1)
  try:
    result = db_connect.execute(alt)
  except Exception, e:
    print "Error while Revoke a remind", e
    return None
  return 1

def delete_a_remind(rid):
  if type(rid) != int:
    return None
  delop = db_remindtable.delete().where(db_remindtable.c.id == rid)
  try:
    result = db_connect.execute(delop)
  except Exception, e:
    print "Error while delete a remind", e
    return None
  return 1

def load_all_guests():
  '''Load All Guest return a dict'''
  retdict = {}
  s = select([db_guest])
  result = db_connect.execute(s)
  if result.rowcount != 0:
    #The Database contain City data
    row = result.fetchone()
    while row != None:
      cur = Flight_Guest(row['id'],row['username'],row['email'])
      retdict[cur.id] = cur
      row = result.fetchone()
    return retdict
  else:
    #The Database contain no City Data
    return retdict

def load_guest_by_id(gid):
  '''RT'''
  s = select([db_guest], and_(db_guest.c.id == gid))
  result = db_connect.execute(s)
  if result.rowcount != 0:
    #The Database contain guest data
    row = result.first()
    cur = Flight_Guest(row['id'],row['username'],row['email'])
    return cur
  else:
    #The Database contain no City Data
    return None


def book_a_flight(gid, fid):
  '''Book A Flight .Check remain generate_a_remind and generate_a_ticket'''
  #Check fid exist
  finfoc = load_flight_by_id(fid)
  fguest = load_guest_by_id(gid)
  if (finfoc == None) or (fguest == None):
    return "Not exist"
  #Query A Posit
  fdict = book_a_seat(fid)
  if fdict == None:
    return "Not available"
  #Generate Remind& Ticket
  ftid = generate_a_ticket()
  frid = generate_a_remind()
  #Prepare a Insert
  ins = db_booktable.insert().values(
    gid = gid,
    fid = fid,
    sid = fdict['sid'],
    tid = ftid,
    rid = frid)
  try:
    result = db_connect.execute(ins)
  except Exception, e:
    print "Error while generate a book", e
    return "Error Insert"
  bid = int(result.inserted_primary_key[0])
  return bid

def delete_a_book(bid):
  '''Delete a item from '''
  if type(bid) != int:
    return None
  s = select([db_booktable], and_(db_booktable.c.id == bid))
  try:
    result = db_connect.execute(s)
  except Exception, e:
    print "Error while query the bid", e
    return None
  if result.rowcount == 0:
    return None
  row = result.first()
  sid = row['sid']
  tid = row['tid']
  rid = row['rid']
  #Prepare delete foreign key reference data
  if DEBUG == True:
    print 'sid = ',sid
    print 'tid = ',tid
    print 'rid = ',rid
  ret1 = 1
  ret2 = 1
  ret3 = 1
  if sid != None:
    sid = int(sid)
    ret3 = revoke_a_seat(sid)

  if tid != None:
    tid = int(tid)
    ret1 = delete_a_ticket(tid)

  if rid != None:
    rid = int(rid)
    ret2 = delete_a_remind(rid)
  

  if (ret1 == None) or (ret2 == None) or (ret3 == None):
    return None
  result.close()
  delop = db_booktable.delete().where(db_booktable.c.id == bid)
  try:
    result = db_connect.execute(delop)
  except Exception, e:
    print "Error while delete a book", e
    return None
  return 1

def load_book_by_id(bid):
  '''Load Book Info from database by id'''
  s = select([db_booktable], and_(db_booktable.c.id == bid))
  result = db_connect.execute(s)
  if result.rowcount == 0:
    result.close()
    return None
  row = result.first()
  bsid = row['sid']
  btid = row['tid']
  brid = row['rid']

  if(bsid == None) or (btid == None) or (brid == None):
    print "Critical Error in Relation At load_book_by_id"
    return None

  s = select([db_flight_seat], and_(db_flight_seat.c.id == bsid))
  tresult = db_connect.execute(s)
  trow = tresult.first()
  tpos = trow['pos']
  s = select([db_tickettable], and_(db_tickettable.c.id == btid))
  sresult = db_connect.execute(s)
  srow = sresult.first()
  sispay = srow['ispay']
  s = select([db_remindtable], and_(db_remindtable.c.id == brid))
  rresult = db_connect.execute(s)
  rrow = rresult.first()
  risget = rrow['isget']

  ret = Flight_Book_Item(
    id = bid,
    gid = row['gid'],
    fid = row['fid'],
    sid = row['sid'],
    tid = row['tid'],
    rid = row['rid'],
    pos = tpos,
    isget = risget,
    ispay = risget,
    )
  return ret




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
  
#Experient Code
if __name__ == "__main__":
  ret = verify_admin('admin','admin')
  ret2 = load_user(ret.id)

  if ret == ret2:
    print 'successful'
  else:
    print 'faild'
    
  # retdict = load_cities()
  # print retdict[1].name
  # print len(retdict)

  ret = book_a_flight(1,1)
  print ret
  retl = load_book_by_id(int(ret))
  print "Info:", retl.fid, retl.isget, retl.ispay, retl.pos


#Load Table From Database complete
