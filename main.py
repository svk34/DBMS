#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Dec 11 13:31:33 2021

@author: abhingude
"""

import pandas as pd
import psycopg2
import streamlit as st
from configparser import ConfigParser
st.set_page_config(layout="wide")
"# American Hospital's Information and Management System"


@st.cache
def get_config(filename="database.ini", section="postgresql"):
    parser = ConfigParser()
    parser.read(filename)
    return {k: v for k, v in parser.items(section)}


@st.cache
def query_db(sql: str):
    # print(f"Running query_db(): {sql}")

    db_info = get_config()

    # Connect to an existing database
    conn = psycopg2.connect(**db_info)

    # Open a cursor to perform database operations
    cur = conn.cursor()

    # Execute a command: this creates a new table
    cur.execute(sql)
    
    # Obtain data
    data = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]

    # Make the changes to the database persistent
    conn.commit()

    # Close communication with the database
    cur.close()
    conn.close()

    df = pd.DataFrame(data=data, columns=column_names)

    return df

#Query1
"### Hospitals in a state which have rating above 4 and have doctors from a specific department"
state_names = "SELECT distinct state FROM Hospital order by state;"
try:
    states = query_db(state_names)["state"].tolist()
    state = st.selectbox("Choose a State", states)
except:
    st.write("Sorry! Something went wrong with your query, please try again.")



dep_names = "SELECT distinct dname FROM Departments order by dname;"
try:
    depts = query_db(dep_names)["dname"].tolist()
    dept = st.selectbox("Choose a Department", depts)
except:
    st.write("Sorry! Something went wrong with your query, please try again.")

if state:
    if dept:
        q1=f"""
        select h.name as hospital , h.street , h.city , h.state , h.zip
        from Hospital h, Departments dep, Doctors doc
        where doc.hid=h.hid
        and doc.dep_id=dep.dep_id
        and h.rating >= 4
        and h.state = '{state}'
        and dep.dname='{dept}';"""
        
        try:
            df1 = query_db(q1)
            st.table(df1)
        except:
            st.write(
            "Sorry! no hospitals match your search criteria."
        )
        
#Query2
"### Hospitals in a state which don't have an ambulance facility"
state_names = "SELECT distinct state FROM Hospital order by state;"
try:
    states = query_db(state_names)["state"].tolist()
    state = st.selectbox("Choose a State ", states)
except:
    st.write("Sorry! Something went wrong with your query, please try again.")

if state:
    q21=f"""
    select count(hid)
    from Hospital
    where hid not in(select distinct hid from Ambulance)
    and state ='{state}'
    group by state;"""
    
    try:
        cnt=query_db(q21)["count"][0]
        st.write(f"There are {cnt} hospitals in {state} which don't have an ambulance facility")
    except:
        st.write(
            "Sorry! Something went wrong with your query, please try again."
        )
    q22=f"""
    select h.name as hospital
    from Hospital h
    where h.hid not in(
    select h.hid 
    from Hospital h , Ambulance a
    where h.hid=a.hid
    group by h.hid
    having count(*)>0)
    and h.state='{state}';"""
    
    try:
        df2=query_db(q22)
        st.table(df2)
    except:
        st.write(
            "Sorry! Something went wrong with your query, please try again."
        )


#Query 3
"### Number of appointments in each department in years : 2020 and 2021"
q31=f"""
select d.dname as Department, count(a.app_id) as Appointments_2020
from departments d , doctors doc , appointments a
where doc.dep_id=d.dep_id
and a.doc_id=doc.doc_id
and extract(year from a.appt_date)=2020
group by d.dep_id 
order by Department;"""
q32=f"""
select d.dname as Department, count(a.app_id) as Appointments_2021
from departments d , doctors doc , appointments a
where doc.dep_id=d.dep_id
and a.doc_id=doc.doc_id
and extract(year from a.appt_date)=2021
group by d.dep_id 
order by Department;"""
try:
    df31=query_db(q31)
except:
    st.write(
        "Sorry! Something went wrong with your query, please try again."
        )
try:
    df32=query_db(q32)
    df3=df31.set_index('department').join(df32.set_index('department'))
    st.table(df3)
except:
        st.write(
            "Sorry! Something went wrong with your query, please try again."
        )
try:
    st.bar_chart(df3)
except:
        st.write(
            "Sorry! Something went wrong with your query, please try again."
        )

#Query4
"### Medicines prescribed to a patient on a particular apoointment date along with their costs"
q41=f"""
select  p.p_name as name
from appointments a , patients p
where a.pid=p.pid
group by p.pid
having count(*)>3
order by p.p_name;"""
try:
    pats = query_db(q41)["name"].tolist()
    patient = st.selectbox("Choose the Patient ", pats)
except:
    st.write("Sorry! Something went wrong with your query, please try again.")

if patient:
    q42=f"""
    select a.appt_date as date
    from appointments a, patients p
    where a.pid=p.pid
    and p.p_name = '{patient}'
    order by a.appt_date;"""
    try:
        ds = query_db(q42)["date"].tolist()
        date1 = st.selectbox("Choose the Appointment Date ", ds)
    except:
        st.write("Sorry! Something went wrong with your query, please try again.")

if date1:
    q43=f"""
    select  m.medicine_name , m.price_per_unit as price_per_unit_in_¢
    from reports_has_medicines rm , medicines m , appointments a , patients p
    where rm.med_id=m.med_id
    and a.app_id=rm.rid
    and a.pid=p.pid
    and a.appt_date='{date1}'
    and p.p_name = '{patient}'
    order by m.medicine_name;"""
    
    try:
        df4=query_db(q43)
        st.table(df4)
    except:
        st.write("Sorry! Something went wrong with your query, please try again.")
    

#Query5
"### Doctors with an MBBS degree working in a particular department and having a minimum experience"   
gen = st.radio(
     "Choose Doctor's Gender",
     ('M','F'))

dep = "SELECT dname FROM departments order by dname;"
try:
    dpts = query_db(dep)["dname"].tolist()
    dept = st.selectbox("Choose Doctor's Department ", dpts)
except:
    st.write("Sorry! Something went wrong with your query, please try again.")
if dept:
    exp = st.slider(
     "Select range of doctor's experience",
     20,60, (20,30))
    v0=exp[0]
    v1=exp[1]
    q5=f"""
    select doc.name as doctor , h.name as hospital, h.street , h.city , h.state
    from doctors doc , hospital h , departments dep
    where doc.hid=h.hid
    and doc.dep_id = dep.dep_id
    and doc.gender='{gen}'
    and doc.experience>='{v0}'
    and doc.experience < '{v1}'
    and dep.dname='{dept}'
    and doc.degree='MBBS'
    order by doc.name;"""
    try:
        df5=query_db(q5)
        st.table(df5)
    except:
        st.write("Sorry! Something went wrong with your query, please try again.")
#Query6
"### Hospital's from a particular state and their revenue in years : 2020 and 2021"
state_names = "SELECT distinct state FROM Hospital order by state;"
try:
    states = query_db(state_names)["state"].tolist()
    state = st.selectbox("Select a State", states)
except:
    st.write("Sorry! Something went wrong with your query, please try again.")

if state:
    q6=f"""
    select h.name as hospital, sum(p.amount) as total_revenue
    from hospital h , payments p
    where h.hid=p.hid
    and h.state='{state}'
    group by h.hid
    order by sum(p.amount) desc;"""

    try:
        df6=query_db(q6)
        st.table(df6)
    except:
        st.write("Sorry! Something went wrong with your query, please try again.")
        
    
#Query7
"### Hospitals and their patient's conditions "
state_names = "SELECT distinct state FROM Hospital order by state;"
try:
    states = query_db(state_names)["state"].tolist()
    state = st.selectbox("Select Hospital's State", states)
except:
    st.write("Sorry! Something went wrong with your query, please try again.")

if state:
    q71=f"""
    select h.name
    from Hospital h , appointments a , doctors d
    where a.doc_id=d.doc_id
    and d.hid=h.hid
    and h.state = '{state}'
    group by h.name 
    having count(*)>2;""" 
    s=0
    try:
        hospitals=query_db(q71)["name"].tolist()   
        hospital = st.selectbox("Select a Hospital",hospitals)
        s=1
    except:
        st.write("Sorry! Something went wrong with your query, please try again.")

    if s:
        q72=f"""
        select r.summary , count(a.pid) as number_of_patients
        from Reports r , appointments a , doctors d ,hospital h
        where r.rid = a.app_id
        and a.doc_id = d.doc_id
        and d.hid=h.hid
        and h.state= '{state}'
        and h.name = '{hospital}'
        group by r.summary
        order by count(a.pid) desc;"""
        try:
            df7=query_db(q72)
            st.table(df7)
        except:
            st.write("Sorry! Something went wrong with your query, please try again.")
    else:
        st.write("Sorry no hospitals match your search criteria")
            




