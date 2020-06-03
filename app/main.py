import os
import tempfile
import traceback

from flask import Flask, render_template
from flask import request, send_file, jsonify

from http import HTTPStatus

from .lib.constants import OUTPUT_FILE
from .backend_intf import main_driver
from .error_handlers import InvalidUsage, InternalError

# Run the app
app = Flask(__name__, static_folder='../build', static_url_path='/')

# Error handlers
@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.errorhandler(InternalError)
def handle_internal_error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

# Views
@app.route("/")
def home_view():
    return app.send_static_file('index.html')


@app.route("/api/test", methods = ["GET"])
def test():
    return jsonify('alive')


@app.route("/api/upload", methods = ["POST"])
def upload():
    try:
        # Extract request parameters and put into dict for backend
        site_info = {}

        # This info is checked on front-end, so they are valid integers
        site_info['maxCapacity'] = int( request.form['maxCapacity'] )
        site_info['numReservedSeating'] = int( request.form['reservedSeating'] )
        site_info['sepRad'] = int( request.form['separationRadius'] )
        site_info['seatWidth'] = int( request.form['seatWidth'] )
        site_info['pewFile'] = request.files['pewFile']
        site_info['familyFile'] = request.files['familyFile']

        # Save snapshot of inputs for error messaging
        inputs = dict(site_info)
        inputs['pewFile'] = inputs['pewFile'].filename
        inputs['familyFile'] = inputs['familyFile'].filename

        # Call backend
        with tempfile.NamedTemporaryFile(mode='w+') as temp_output_file, \
                tempfile.NamedTemporaryFile(mode='w+') as pew_file, \
                tempfile.NamedTemporaryFile(mode='w+') as family_file:
            request.files['pewFile'].save( pew_file.name )
            request.files['familyFile'].save( family_file.name )
            site_info['pewFile'] = (pew_file, request.files['pewFile'].filename)
            site_info['familyFile'] = (family_file, request.files['familyFile'].filename)
            main_driver( site_info, temp_output_file )

            # Stream file object back
            temp_output_file.seek(0)
            return send_file( temp_output_file.name, as_attachment=True )
    except InvalidUsage:
        raise # Let InvalidUsage propagate up the stack.
    except:
        message = ("A fatal server error has occurred. Please relay the entirety"
                   " of this message to a developer.")
        error = {
            'trace': traceback.format_exc(),
            'inputs': inputs,
        }
        raise InternalError(message, error)
