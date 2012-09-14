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

def load_cities():
  '''Load All City Info from database,return a dict`'''
  retdict = {}
  s = select([db_city])
  result = db_connect.execute(s)
  if result.returns_rows == True:
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
  if result.returns_rows == True:
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
  if result.returns_rows == True:
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
  if result.returns_rows == True:
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

def verify_admin(name, password):
  '''Verify the Administrator User from database'''
  s = select([db_admin], and_(db_admin.c.name == name, db_admin.c.password == password))
  result = db_connect.execute(s)
  #Get Database Query Results
  if result.returns_rows == True:
    #Admin Verify OK
    print "return rows:", result.returns_rows
    print "rows count", result.rowcount
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

ret = verify_admin('admin','admin')
ret2 = load_user(ret.id)

if ret == ret2:
  print 'successful'
else:
  print 'faild'
  
# retdict = load_cities()
# print retdict[1].name
# print len(retdict)

citydic = load_cities()
newflight = Flight_Infoc(
  id = 50,
  fname = u"CZ384",
  ffrom = citydic[5],
  fto = citydic[6],
  fset = Flight_Time(30,15),
  fdur = Flight_Time(00,2),
  farr = None,
  fsetday = Flight_Day(4,9,2012),
  fprice = 600,
  fseat = None)

ret = insert_flight_info(newflight)
newflight.id = 0
newflight.fname = u"XZ384"
ret = alter_flight_info(newflight)
#Load Table From Database complete
