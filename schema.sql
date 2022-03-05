DROP TABLE IF EXISTS Hospital;
DROP TABLE IF EXISTS Departments;
DROP TABLE IF EXISTS Doctors;
DROP TABLE IF EXISTS Staff;
DROP TABLE IF EXISTS Ambulance;
DROP TABLE IF EXISTS Medicines;
DROP TABLE IF EXISTS Patients;
DROP TABLE IF EXISTS Payments;
DROP TABLE IF EXISTS Reports;
DROP TABLE IF EXISTS Reports_has_Medicines;
DROP TABLE IF EXISTS Appointments;


CREATE TABLE Hospital(
hid integer primary key,
name varchar(128) not null,
street varchar(128) not null,
city varchar(128) not null,
state varchar(2) not null,
zip integer not null,
rating integer,
check (rating in (0,1,2,3,4,5)),
hospital_license integer not null unique
);




CREATE TABLE Departments(
dep_id integer primary key,
dname varchar(64) not null
);


CREATE TABLE Doctors(
doc_id integer primary key,
name varchar(128) not null,
gender char(1) ,
check (gender in ('M', 'F')),
dob date,
degree varchar(64) ,
success_rate integer ,
experience integer ,
hid integer not null,
dep_id integer not null,
foreign key (hid) references Hospital(hid),
foreign key (dep_id) references Departments(dep_id)
);




CREATE TABLE Staff(
sid integer primary key, 
name varchar(128) not null,
dob date ,
experience integer,
salary integer,
dep_id integer not null,
hid integer not null,
foreign key (hid) references Hospital(hid),
foreign key (dep_id) references Departments(dep_id)
);



CREATE TABLE Ambulance(
aid integer primary key,
vehicle_no varchar(10),
vehicle_type varchar(128),
hid integer not null,
foreign key (hid) references Hospital(hid)
);


CREATE TABLE Medicines(
med_id integer primary key,
medicine_name varchar(128) not null,
price_per_unit decimal
);

CREATE TABLE Reports(
rid integer primary key,
summary varchar(128)
);

CREATE TABLE Reports_has_Medicines(
rid integer ,
med_id integer,
primary key(rid,med_id),
foreign key (med_id) references Medicines(med_id),
foreign key (rid) references Reports(rid)
);

CREATE TABLE Patients(
pid integer primary key,
p_name varchar(128) not null,
gender char(1) ,
check (gender in ('M', 'F')),
state varchar(2) not null,
dob date,
insurance bool not null
);


CREATE TABLE Appointments(
app_id integer primary key,
appt_date date not null,
rid integer unique not null,
pid integer not null,
doc_id integer not null,
foreign key (rid) references Reports(rid),
foreign key (pid) references Patients(pid),
foreign key (doc_id) references Doctors(doc_id)
);



CREATE TABLE Payments(
tid integer,
hid integer ,
pid integer,
amount integer not null, 
date date not null,
primary key(tid,pid,hid),
foreign key (pid) references Patients(pid),
foreign key (hid) references Hospital(hid)
);

/*
Queries
1 Hospitals in state which have rating >4 and having doctors from specific department
2 Count of Hospitals in state which don't have ambulance facility in a particular state
3 Appointments made by a specific department during differemt years
4 Medicines recieved by a patient during a particular appointment and their cost     
5 Gender , department doctors who have an experience of more than years of experience and have an MBBS degree 
6 Hospitals and their revenue in a particualr state 
7 Department's Average staff salary for each state. */