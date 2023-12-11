from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base

app = Flask(__name__)

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

@app.route("/")
def home():
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).all()
    session.close()

    precipitation = {date: prcp for date, prcp in results}
    return jsonify(precipitation)

@app.route("/api/v1.0/precipitation_data")
def precipitation_data():
    session = Session(engine)

    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= func.date(recent_date, '-12 months')).\
        order_by(Measurement.date).all()

    precipitation_data = {date: prcp for date, prcp in results}
    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    # returns jsonified data of all of the stations in the database
    total_stations = session.query(Measurement.station,
                              func.count(Measurement.id)).group_by(Measurement.station).order_by(func.count(Measurement.id).desc()).all()
    session.close()

    stations = [station[0] for station in total_stations]
    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    # Returns jsonified data for the most active station (USC00519281)
    total_stations = session.query(Measurement.station,
                              func.count(Measurement.id)).group_by(Measurement.station).order_by(func.count(Measurement.id).desc()).all()
    most_active_station = total_stations[0][0]
    recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    results = session.query(Measurement.date, Measurement.tobs).\
              filter(Measurement.station == most_active_station).\
              filter(Measurement.date >= func.date(recent_date, '-12 months')).all()
    session.close()

    # Convert results to a suitable format and return JSON
    tobs_data = {date: tobs for date, tobs in results}
    return jsonify(tobs_data)

@app.route("/api/v1.0/<start>")
def temp_start(start):
    session = Session(engine)
    # Returns the min, max, and average temperatures calculated from the given start date to the end of the dataset 
    results = session.query(func.min(Measurement.tobs), 
                    func.max(Measurement.tobs), 
                    func.avg(Measurement.tobs)).\
                    filter(Measurement.date >= start).all()
    
    session.close()
    temp_st={}
    temp_st["Min_Temp"]=results[0][0]
    temp_st["avg_Temp"]=results[0][1]
    temp_st["max_Temp"]=results[0][2]
    return jsonify(temp_st)

    
@app.route("/api/v1.0/<start>/<end>")
def temp_range(start, end):
    session = Session(engine)
    # Returns the min, max, and average temperatures calculated from the given start date to the given end date
    results = session.query(func.min(Measurement.tobs), 
                    func.max(Measurement.tobs), 
                    func.avg(Measurement.tobs)).\
                    filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    
    session.close()
    temp_data={}
    temp_data["Min_Temp"]=results[0][0]
    temp_data["avg_Temp"]=results[0][1]
    temp_data["max_Temp"]=results[0][2]
    return jsonify(temp_data)

if __name__ == '__main__':
    app.run()
