# Import the dependencies.
from flask import Flask, jsonify
import datetime as dt
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

#################################################
# Database Setup
#################################################


# reflect an existing database into a new model
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################


@app.route("/")
def home():
    return (
        f"Welcome to the Climate App API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation - Precipitation data for the last 12 months<br/>"
        f"/api/v1.0/stations - List of stations<br/>"
        f"/api/v1.0/tobs - Temperature observations for the most active station in the last year<br/>"
        f"/api/v1.0/start_date - Min, Max, and Avg temperatures from a start date (YYYY-MM-DD)<br/>"
        f"/api/v1.0/start_date/end_date - Min, Max, and Avg temperatures between start and end dates (YYYY-MM-DD)"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculate the date one year ago from the last date in the database
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    most_recent_date = dt.datetime.strptime(most_recent_date, "%Y-%m-%d")
    one_year_ago = most_recent_date - dt.timedelta(days=365)

    # Query precipitation data for the last 12 months
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_ago).all()

    # Convert the query results to a dictionary
    precipitation_data = {}
    for date, prcp in results:
        precipitation_data[date] = prcp

    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def stations():
    # Query list of stations
    results = session.query(Station.station).all()

    # Convert the query results to a list
    station_list = [station[0] for station in results]

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    # Query temperature observations for the most active station in the last year
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == most_active_station_id).filter(Measurement.date >= one_year_ago).all()

    # Convert the query results to a list of dictionaries
    temperature_list = [{"Date": date, "Temperature": tobs} for date, tobs in results]

    return jsonify(temperature_list)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temperature_stats(start, end=None):
    try:
        # Convert start and end date strings to datetime objects
        start_date = dt.datetime.strptime(start, "%Y-%m-%d")
        if end:
            end_date = dt.datetime.strptime(end, "%Y-%m-%d")
        else:
            end_date = most_recent_date
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

    # Query min, max, and avg temperatures for the specified date range
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    # Convert the query results to a dictionary
    temperature_stats = {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "min_temperature": results[0][0],
        "max_temperature": results[0][1],
        "avg_temperature": results[0][2]
    }

    return jsonify(temperature_stats)

if __name__ == "__main__":
    app.run(debug=True)