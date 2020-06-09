from flask import Flask, jsonify
import pandas as pd
#import sqlalchemy
from sqlalchemy import create_engine

#setup database 
engine = create_engine("sqlite:///hawaii.sqlite")

station = pd.read_sql("SELECT * FROM station", engine)
measurement = pd.read_sql("SELECT * FROM measurement", engine)


#Convert the query results to a dictionary 
precipitation = dict(zip(measurement.date, measurement.prcp))
stations = dict(zip(station.id, station.station))

#find most active station temps
query = '''
SELECT date, tobs FROM measurement
WHERE station IN
(SELECT station FROM
(SELECT station, max(count) FROM
	(SELECT 
		station,
		count(station) as count
	FROM measurement
	GROUP BY station)))
'''

most_active_station_temps = pd.read_sql(query, engine)


#Flask Setup
app = Flask(__name__)

#List all available api routes
@app.route("/")
def welcome():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start/YYYY-MM-DD<br/>"
        f"/api/v1.0/start/end/YYYY-MM-DD/YYYY-MM-DD")


#Return the JSON representation of percipitation dictionary
@app.route("/api/v1.0/precipitation")
def prcp():
    return jsonify(precipitation)


#Return the JSON representation of stations 
@app.route('/api/v1.0/stations')
def station():
    return stations


#Return the JSON representation of tobs for most active station
@app.route('/api/v1.0/tobs')
def tobs():
    results_json = most_active_station_temps.to_json(orient='records')   
    return jsonify(results_json)


#Calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date
@app.route('/api/v1.0/start/<start>')
def start_date(start):
    query = f"SELECT MIN(tobs) as 'Min Temp', MAX(tobs) as 'Max Temp', AVG(tobs) as 'Avg Temp' FROM measurement WHERE date >= '{start}'"
    results = pd.read_sql(query, engine)
    results_json = results.to_json(orient='records')   
    return jsonify(results_json)

    
#When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive
@app.route('/api/v1.0/start/end/<start>/<end>')
def start_end_date(start,end):
    query = f"SELECT MIN(tobs) as 'Min Temp', MAX(tobs) as 'Max Temp', AVG(tobs) as 'Avg Temp' FROM measurement WHERE date >= '{start}' AND date <= '{end}'"
    results = pd.read_sql(query, engine)
    results_json = results.to_json(orient='records')
   
    return jsonify(results_json)


if __name__ == "__main__":
    app.run(debug=True)
 
    
 
   