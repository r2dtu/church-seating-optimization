import os
import tempfile

from flask import Flask, render_template
from flask import request, send_file, jsonify

from http import HTTPStatus

from .lib.constants import OUTPUT_FILE
from .backend_intf import main_driver

# Run the app
app = Flask(__name__, static_folder='../build', static_url_path='/')

@app.route("/")
def home_view():
    return app.send_static_file('index.html')

@app.route("/api/test", methods = ["GET"])
def test():
    return jsonify('alive')

@app.route("/api/upload", methods = ["POST"])
def upload():
    # Extract request parameters and put into dict for backend
    site_info = {}

    # This info is checked on front-end, so they are valid integers
    site_info['maxCapacity'] = int( request.form['maxCapacity'] )
    site_info['numReservedSeating'] = int( request.form['reservedSeating'] )
    site_info['sepRad'] = int( request.form['separationRadius'] )
    site_info['seatWidth'] = int( request.form['seatWidth'] )

    # Make tmp files for CSV inputs
    handle, site_info['pewFile'] = tempfile.mkstemp()
    os.close( handle )
    request.files['pewFile'].save( site_info['pewFile'] )
    handle, site_info['familyFile'] = tempfile.mkstemp()
    os.close( handle )
    request.files['familyFile'].save( site_info['familyFile'] )

    # Call backend
    with tempfile.NamedTemporaryFile(mode='w+') as temp_output_file, open( site_info['pewFile'] ) as pew_file, open( site_info['familyFile'] ) as family_file:
        site_info['pewFile'] = open( site_info['pewFile'] )
        site_info['familyFile'] = open( site_info['familyFile'] )
        err_msg, status_code = main_driver( site_info, temp_output_file )

        if status_code == HTTPStatus.OK:
            # Stream file object back
            temp_output_file.seek(0)
            return send_file( temp_output_file.name, as_attachment=True )

        else:
            return jsonify( err_msg ), status_code
