# 1. import Flask and dependencies
import numpy as np
import pandas as pd 
import datetime as dt 

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)


# print(Base.classes.keys())





# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station
#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"Stations: /api/v1.0/stations<br/>"
        f"Data for most active station for last year: /api/v1.0/tobs<br/>"
        f"Min temp, avg temp, and max temp for a given start date: /api/v1.0/yyyy-mm-dd<br/>"
        f"Min temp, avg temp, and max temp for a given start and end dates: /api/v1.0/yyyy-mm-dd/yyyy-mm-dd"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    sel = [Measurement.date,Measurement.prcp]
    results = session.query(*sel).all()

    session.close()

    # Convert into dictionary
    precipitation = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["Date"] = date
        prcp_dict["Precipitation"] = prcp
        precipitation.append(prcp_dict)

    return jsonify(precipitation)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    sel = [Station.station,Station.name,Station.latitude,Station.longitude,Station.elevation]
    results = session.query(*sel).all()

    session.close()
    # Convert into dictionary
    stations = []
    for station,name,lat,lon,el in results:
        station_dict = {}
        station_dict["Station"] = station
        station_dict["Name"] = name
        station_dict["Lat"] = lat
        station_dict["Lon"] = lon
        station_dict["Elevation"] = el
        stations.append(station_dict)

    return jsonify(stations)


@app.route("/api/v1.0/<start>")
def start_date(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    results = session.query(*sel).\
              filter(Measurement.date >= year_ago).\
              order_by(Measurement.date).all()

    session.close()
    # Convert into dictionary
    tobs_df = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict[date] = tobs
        tobs_df.append(tobs_dict)

    

    return jsonify(tobs_df)


@app.route("/api/v1.0/tobs")
def tobs():
    # * Query the dates and temperature observations of the most active station for the last year of data.
    # Create our session (link) from Python to the DB
    session = Session(engine)

    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date_dt = dt.datetime.strptime(last_date[0], '%Y-%m-%d')
    year_ago = dt.date(last_date_dt.year -1, last_date_dt.month, last_date_dt.day)
    
    sel = [Measurement.date, Measurement.tobs]
    results = session.query(*sel).\
              filter(Measurement.date >= year_ago).\
              filter(Measurement.station == 'USC00519281').\
              order_by(Measurement.date).all()

    session.close()
    # Convert into dictionary
    tobs_df = []
    for date, tobs in results:
        tobs_dict = {}
        tobs_dict[date] = tobs
        tobs_df.append(tobs_dict)

    

    return jsonify(tobs_df)







if __name__ == '__main__':
    app.run(debug=True)