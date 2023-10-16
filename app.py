# Import the dependencies.
import datetime as dt
import numpy as np
import pandas as pd
import re

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy.inspection import inspect
from sqlalchemy import create_engine, func, Date, DateTime 

from flask import Flask, jsonify
 
#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

################################################
#Reflect an existing database into a new model
#################################################

Base = automap_base()

################################################
# Reflect the Tables
#################################################

Base.prepare(autoload_with=engine)

################################################
# Save references to each table
#################################################

Measurement = Base.classes.measurement
Station = Base.classes.station


#######################################################
# Create our session (link) from Python to the DataBase
#######################################################

session = Session(engine)

################################################
# Flask Setup
#################################################

app = Flask(__name__)

################################################
# Flask routes
#################################################

#1. "/"
# - Start at the homepage.

# - List all the available routes.

@app.route("/")
def welcom():
    return(
        f"Welcome to Hawaii Climate ANalysis API<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start<br/>"
        f"/api/v1.0/temp/start/end<br/>"
        f"<p> 'start and end date should be in the format MMDDYYYY.</p>"
    )

#  Precipitation Analysis

#2. /api/v1.0/precipitation

# - Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) 
#   to a dictionary using date as the key and prcp as the value.
# - Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    One_year=dt.date(2017,8,23) - dt.timedelta(days=365)
    
    precipitation=session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_dt).order_by(Measurement.date.desc).all()
    session.close()
    
    precip = {date:prcp for date, prcp in precipitation}

    return jsonify(precip)


#3. /api/v1.0/stations

#  Return a JSON list of stations from the dataset.

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
        
    Station_results = session.query(Station.station).all()

    session.close()

    stations = list(np.ravel(Station_results))
    
    return jsonify(stations)

#4. /api/v1.0/tobs

# - Query the dates and temperature observations of the most-active station for the previous year of data.
# - Return a JSON list of temperature observations for the previous year.

@app.route("/api/v1.0/tobs")
def temp_monthly():
    session=Session(engine)
    prev_year_dt=dt.date(2017,8,23) - dt.timedelta(days=365)
    temp_query=session.query(Measurement.tobs).\
        filter(Measurement.station=='USC00519281').\
        filter (Measurement.date >= prev_year_dt).all()
    session.close()

    temperature = list(np.ravel(temp_query))
    
    return jsonify(tob_observation)

#5.  /api/v1.0/<start> and /api/v1.0/<start>/<end>

#   Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start or start-end range.

#   For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.

#   For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.

@app.route("/api/v1.0/temp/<start>")

@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    selection = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if not end:
        start=dt.datetime.strptime(start, "%m%d%Y")
        results = session.query(*selection).filter(Measurement.date >=start).all()
        session.close()
        temps = list(np.ravel(results))
 
        return jsonify(temps) 
        
    start = dt.datetime.strptime(start, "%m%d%Y")
    end = dt.datetime.strptime(end, "%m%d%Y")
    results = session.query(*selection).\
        filter(Measurement.date >= start).\
        filter( Measurement.date <= end).all()
        
    session.close()
    Temps = list(np.ravel(results))
 
    return jsonify(Temps)

if __name__=="__main__":
    app.run(debug=True)
    