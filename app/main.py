from flask import Flask, render_template
from flask import request, stream_with_context, Response

from church_seating import main_driver

app = Flask(__name__)

@app.route("/")
def home_view():
    return render_template("index.html",
                           title="Church Seating Optimization",
                           description="WUTWUT")

@app.route("/upload", methods = ["POST"])
def upload():
    maxCapacity = request.form['maxCapacity']
    numReservedSeating = request.form['numReservedSeating']
    sepRad = request.form['sepRad']
    seatWidth = request.form['seatWidth']
    pewFile = request.files['pewFile']
    familyFile = request.files['familyFile']

    # Call backend
    seat_arr_str = main_driver(pewFile, familyFile, maxCapacity,
                               numReservedSeating, sepRad, seatWidth)

    # Stream file object back
    return Response( seat_arr_str, mimetype='text/csv',
                     headers={"Content-Disposition": 
                     "attachment; filename=seating_arrangement.csv"})
