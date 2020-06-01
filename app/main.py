import os
import tempfile

from flask import Flask, render_template
from flask import request, send_file

from .lib.constants import OUTPUT_FILE
from .backend_intf import main_driver

# Run the app
app = Flask(__name__)

@app.route("/")
def home_view():
    return render_template("index.html",
                           title="Church Seating Optimization",
                           description="You have found an Easter Egg LOL")

@app.route("/upload", methods = ["POST"])
def upload():
    # Extract request parameters and put into dict for backend
    site_info = {}

    # This info is checked on front-end, so they are valid integers
    site_info['maxCapacity'] = int( request.form['maxCapacity'] )
    site_info['numReservedSeating'] = int( request.form['numReservedSeating'] )
    site_info['sepRad'] = int( request.form['sepRad'] )
    site_info['seatWidth'] = int( request.form['seatWidth'] )

    # Make tmp files for CSV inputs
    handle, site_info['pewFile'] = tempfile.mkstemp()
    os.close( handle )
    request.files['pewFile'].save( site_info['pewFile'] )
    handle, site_info['familyFile'] = tempfile.mkstemp()
    os.close( handle )
    request.files['familyFile'].save( site_info['familyFile'] )

    # Call backend
    try:
        main_driver( site_info, 'app/' + OUTPUT_FILE )

        # Stream file object back
        return send_file( OUTPUT_FILE, as_attachment=True )

    except Exception as e:
        print( e )
        return e
