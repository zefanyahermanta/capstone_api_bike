from flask import Flask, request
import sqlite3
import requests
from tqdm import tqdm
import json 
import numpy as np
import pandas as pd
app = Flask(__name__) 

@app.route('/')
@app.route('/homepage')
def home():
    return 'Hello World'

@app.route('/stations/')
def route_all_stations():
    conn = make_connection()
    stations = get_all_stations(conn)
    return stations.to_json()

@app.route('/trips/')
def route_all_trips():
    conn = make_connection()
    trips = get_all_trips(conn)
    return trips.to_json()

@app.route('/stations/<station_id>')
def route_stations_id(station_id):
    conn = make_connection()
    station = get_station_id(station_id, conn)
    return station.to_json()
    
@app.route('/trips/<trips_id>')
def route_trips_id(trips_id):
    conn = make_connection()
    trips = get_trip_id(trips_id, conn)
    return trips.to_json()

@app.route('/json',methods=['POST']) 
def json_example():
    
    req = request.get_json(force=True) # Parse the incoming json data as Dictionary
    
    name = req['name']
    age = req['age']
    address = req['address']
    
    return (f'''Hello {name}, your age is {age}, and your address in {address}
            ''')


@app.route('/stations/add', methods=['POST']) 
def route_add_station():
    # parse and transform incoming data into a tuple as we need 
    data = pd.Series(eval(request.get_json(force=True)))
    data = tuple(data.fillna('').values)
    
    conn = make_connection()
    result = insert_into_stations(data, conn)
    return result

@app.route('/trips/add', methods=['POST']) 
def route_add_trip():
    # parse and transform incoming data into a tuple as we need 
    data = pd.Series(eval(request.get_json(force=True)))
    data = tuple(data.fillna('').values)
    
    conn = make_connection()
    result = insert_into_trips(data, conn)
    return result

@app.route('/trips/average_duration_bike') ## Static (1)
def route_trips_avgDur():
    conn = make_connection()
    trips = get_trip_durationbike(conn)
    return trips.to_json()

@app.route('/trips/total_duration/<bike_id>') ## Dynamic (2)
def route_total_duration(bike_id):
    conn = make_connection()
    average_duration = get_trip_durationbike_id(bike_id, conn)
    return average_duration.to_json()

@app.route('/period_stasions',methods=['POST']) ## post (3)
def route_period_stasions():
    input_data = request.get_json(force=True)
    #print(input_data)
    ##input_data = tuple(input_data.)
    ##specified_date='2015'
    specified_date = input_data['period'] # Select specific items (period) from the dictionary (the value will be "2015-08")
    #print(specified_date)
    conn = make_connection()
    result = get_trips_date(specified_date,conn).groupby('start_station_id').agg({
        'bikeid' : 'count', 
        'duration_minutes' : 'mean'
    })
    return result.to_json()


######################################################################################

def get_trips_date(specified_date,conn):   
    query = f"""SELECT * FROM trips WHERE start_time LIKE ('{specified_date}%')"""
    selected_data = pd.read_sql_query(query, conn)
    return selected_data
    #result=selected_data


def get_trip_durationbike_id(bike_id, conn):
    query = f"""SELECT bikeid , subscriber_type, SUM(duration_minutes) as TOTAL_DURATION
FROM trips
WHERE  bikeid = {bike_id}"""
    result = pd.read_sql_query(query, conn)
    return result


def get_trip_durationbike(conn):
    query = f"""SELECT bikeid , subscriber_type, AVG(duration_minutes) as AVG_DURATION
FROM trips
WHERE subscriber_type = 'Local365' AND start_time LIKE '2016%'
group by bikeid
ORDER by AVG_DURATION DESC"""
    result = pd.read_sql_query(query, conn)
    return result


def get_all_stations(conn):
    query = f"""SELECT * FROM stations"""
    result = pd.read_sql_query(query, conn)
    return result

def get_all_trips(conn):
    query = f"""SELECT * FROM trips """
    result=pd.read_sql_query(query,conn)
    return result

def get_station_id(station_id, conn):
    query = f"""SELECT * FROM stations WHERE station_id = {station_id}"""
    result = pd.read_sql_query(query, conn)
    return result 

def get_trip_id(trip_id, conn):
    query = f"""SELECT * FROM trips WHERE id = {trip_id}"""
    result = pd.read_sql_query(query, conn)
    return result

def make_connection():
    connection = sqlite3.connect('austin_bikeshare.db')
    return connection

def insert_into_stations(data, conn):
    query = f"""INSERT INTO stations values {data}"""
    try:
        conn.execute(query)
    except:
        return 'Error'
    conn.commit()
    return 'OK'

def insert_into_trips(data, conn):
    query = f"""INSERT INTO trips values {data}"""
    try:
        conn.execute(query)
    except:
        return 'Error'
    conn.commit()
    return 'OK'


if __name__ == '__main__':
    app.run(debug=True, port=5000)
