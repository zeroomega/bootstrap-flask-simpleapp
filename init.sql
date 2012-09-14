-- 建立数据库
CREATE DATABASE dbproj;

-- 建立访问用户
GRANT ALL ON dbproj.* TO 'bootstrap'@'localhost' IDENTIFIED BY 'boot';

-- 进入数据库dbproj
USE dbproj;

-- 建立相应的数据表
-- 建立城市信息表
CREATE TABLE city (
  id int AUTO_INCREMENT,
  name VARCHAR(40) UNIQUE NOT NULL,
  PRIMARY KEY (id)
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
  
-- 建立航班信息表
CREATE TABLE flight_info (
  id int PRIMARY KEY AUTO_INCREMENT,
  flight VARCHAR(40) UNIQUE NOT NULL,
  cfrom int,
  cto int,
  set_min int,
  set_hour int,
  set_day int,
  set_mon int,
  set_year int,
  dur_min int,
  dur_hour int,
  price int,
  seat int, 
  CONSTRAINT fi1 FOREIGN KEY (cfrom) REFERENCES city (id)
  ON DELETE SET NULL
  ON UPDATE SET NULL,
  CONSTRAINT fi2 FOREIGN KEY (cto) REFERENCES city (id)
  ON DELETE SET NULL
  ON UPDATE SET NULL
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
  
-- 座位预订
CREATE TABLE flight_seat (
  id int PRIMARY KEY AUTO_INCREMENT,
  fid int,
  pos int,
  CONSTRAINT fs FOREIGN KEY (fid) REFERENCES flight_info (id)
  ON DELETE CASCADE
  ON UPDATE SET NULL
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
  
-- 管理员
CREATE TABLE admin (
  id int PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(20),
  password VARCHAR(100)
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
  
-- 旅客
CREATE TABLE guest (
  id int PRIMARY KEY AUTO_INCREMENT,
  username VARCHAR(20),  
  password VARCHAR(100),
  email VARCHAR(100)
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
  
CREATE TABLE ticket_table (
  id int PRIMARY KEY AUTO_INCREMENT,  
  ispay int DEFAULT 0
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE remind_table (
  id int PRIMARY KEY AUTO_INCREMENT,
  isget int DEFAULT 0
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8;
  
-- 订票信息
CREATE TABLE booktable (
  id int PRIMARY KEY AUTO_INCREMENT,
  gid int,
  fid int,
  sid int,
  tid int,
  rid int,
  CONSTRAINT bt0 FOREIGN KEY (gid) REFERENCES guest (id)
  ON DELETE SET NULL
  ON UPDATE SET NULL,
  CONSTRAINT bt1 FOREIGN KEY (fid) REFERENCES flight_info(id)
  ON DELETE SET NULL
  ON UPDATE SET NULL,
  CONSTRAINT bt2 FOREIGN KEY (sid) REFERENCES flight_seat(id)
  ON DELETE SET NULL
  ON UPDATE SET NULL,
  CONSTRAINT bt3 FOREIGN KEY (tid) REFERENCES ticket_table(id)
  ON DELETE SET NULL
  ON UPDATE SET NULL,
  CONSTRAINT bt4 FOREIGN KEY (rid) REFERENCES remind_table(id)
  ON DELETE SET NULL
  ON UPDATE SET NULL
  ) ENGINE=InnoDB DEFAULT CHARSET=utf8;

  
-- 填充数据
-- 城市名称
INSERT INTO city(id,name) VALUES(1,'北京');
INSERT INTO city(id,name) VALUES(2,'天津');
INSERT INTO city(id,name) VALUES(3,'上海');
INSERT INTO city(id,name) VALUES(4,'武汉');
INSERT INTO city(id,name) VALUES(5,'厦门');
INSERT INTO city(id,name) VALUES(6,'深圳');
INSERT INTO city(id,name) VALUES(7,'海口');
INSERT INTO city(id,name) VALUES(8,'杭州');
INSERT INTO city(id,name) VALUES(9,'长沙');
INSERT INTO city(id,name) VALUES(10,'重庆');

-- 航班信息
INSERT INTO flight_info(id, flight, cfrom, cto, set_min, set_hour, set_day, set_mon, set_year, dur_min, dur_hour,price, seat) 
VALUES(1, 'ZH001', 1, 3, 0, 11, 1, 9, 2012, 30, 2, 1500, 180);

INSERT INTO flight_info(id, flight, cfrom, cto, set_min, set_hour, set_day, set_mon, set_year, dur_min, dur_hour,price, seat) 
VALUES(2, 'CZ001', 2, 4, 30, 15, 2, 9, 2012, 00, 2, 1500, 180);

-- Administrator Info
INSERT INTO admin(name,password) values('admin','admin');

-- Guest Info
INSERT INTO guest(id, username, password, email) VALUES(1,'Alpha', 'Alpha', 'alpha@a.com');
INSERT INTO guest(id, username, password, email) VALUES(2,'Bravo', 'Bravo', 'bravo@a.com');
INSERT INTO guest(id, username, password, email) VALUES(3,'Charlie', 'Charlie', 'charlie@a.com');
INSERT INTO guest(id, username, password, email) VALUES(4,'Delta', 'Delta', 'delta@a.com');
INSERT INTO guest(id, username, password, email) VALUES(5,'Echo', 'Echo', 'echo@a.com');
INSERT INTO guest(id, username, password, email) VALUES(6,'Foxtrot', 'Foxtrot', 'foxtrot@a.com');
INSERT INTO guest(id, username, password, email) VALUES(7,'Golf', 'Golf', 'golf@a.com');
INSERT INTO guest(id, username, password, email) VALUES(8,'Hotel', 'Hotel', 'hotel@a.com');
INSERT INTO guest(id, username, password, email) VALUES(9,'India', 'India', 'india@a.com');
INSERT INTO guest(id, username, password, email) VALUES(10,'Juliet', 'Juliet', 'juliet@a.com');
INSERT INTO guest(id, username, password, email) VALUES(11,'Kilom', 'Kilom', 'kilom@a.com');
INSERT INTO guest(id, username, password, email) VALUES(12,'Lima', 'Lima', 'lima@a.com');
INSERT INTO guest(id, username, password, email) VALUES(13,'Mike', 'Mike', 'mike@a.com');
INSERT INTO guest(id, username, password, email) VALUES(14,'November', 'November', 'november@a.com');
INSERT INTO guest(id, username, password, email) VALUES(15,'Oscar', 'Oscar', 'oscar@a.com');
INSERT INTO guest(id, username, password, email) VALUES(16,'Papa', 'Papa', 'papa@a.com');
INSERT INTO guest(id, username, password, email) VALUES(17,'Quebec', 'Quebec', 'quebec@a.com');
INSERT INTO guest(id, username, password, email) VALUES(18,'Romeo', 'Romeo', 'romeo@a.com');
INSERT INTO guest(id, username, password, email) VALUES(19,'Sierra', 'Sierra', 'sierra@a.com');
INSERT INTO guest(id, username, password, email) VALUES(20,'Tango', 'Tango', 'tango@a.com');
INSERT INTO guest(id, username, password, email) VALUES(21,'Uniform', 'Uniform', 'uniform@a.com');
INSERT INTO guest(id, username, password, email) VALUES(22,'Victor', 'Victor', 'victor@a.com');
INSERT INTO guest(id, username, password, email) VALUES(23,'Whiskey', 'Whiskey', 'whiskey@a.com');
INSERT INTO guest(id, username, password, email) VALUES(24,'Xray', 'Xray', 'xray@a.com');
INSERT INTO guest(id, username, password, email) VALUES(25,'Yankee', 'Yankee', 'yankee@a.com');
INSERT INTO guest(id, username, password, email) VALUES(26,'Zulu', 'Zulu', 'zulu@a.com');

-- 