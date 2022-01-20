# Imports
from flask import Flask, request, Response
import json, os, requests

# Create app
app = Flask(__name__)

# Storage data structure
key_dict = dict()

# Get instance type
forward_add = None
if os.environ.get('FORWARDING_ADDRESS'):
    forward_add = os.environ.get('FORWARDING_ADDRESS')
print(forward_add)

# Functions
@app.route('/key-value-store')
def base_path():
    return 'Does nothing'

if not forward_add:
    @app.route('/key-value-store/<key>', methods=['GET', 'PUT', 'DELETE'])
    def key_func(key):
        #app.logger.info(request.__dict__)
        #app.logger.info(request.get_json())
        resp_json = dict()
        status = 405
        if request.method == 'GET':
            if key in key_dict:
                resp_json = {
                    "doesExist": True, 
                    "message": "Retrieved successfully", 
                    "value": key_dict[key]
                }
                status = 200
            else:
                resp_json = {
                    "doesExist": False, 
                    "error": "Key does not exist", 
                    "message": "Error in GET"
                    }
                status = 404
            return Response(json.dumps(resp_json), status, mimetype="application/json")
        elif request.method == 'PUT':
            req_json = request.get_json()
            if 'value' not in req_json or key is None:
                resp_json = {
                    'error':'Value is missing',
                    'message':'Error in PUT'
                }
                status = 400
            elif len(key) > 50:
                resp_json = {
                    'error':'Key is too long',
                    'message':'Error in PUT'
                }
                status = 400
            elif key not in key_dict:
                key_dict[key] = req_json["value"]
                resp_json = {
                    'message':'Added successfully',
                    'replaced':False
                }
                status = 201
            else:
                key_dict[key] = req_json["value"]
                resp_json = {
                    'message':'Updated successfully', 
                    'replaced':True
                }
                status = 200
            return Response(json.dumps(resp_json), status, mimetype='application/json')
        elif request.method == 'DELETE':
            if key in key_dict:
                del key_dict[key]
                resp_json = {
                    'doesExist' : True,
                    'message'   : 'Deleted successfully'
                }
                status = 200
            else:
                resp_json = {
                    'doesExist' : False,
                    'error'     : 'Key does not exist',
                    'message'   : 'Error in DELETE'
                }
                status = 404
            return Response(json.dumps(resp_json), status, mimetype='application/json')
        return 'This method is unsupported.'
else:
    @app.route('/key-value-store/<key>', methods=['GET', 'PUT', 'DELETE'])
    def key_func(key):
        forward_resp = None
        error_resp = {
            'error': 'Main instance is down'
        }
        if request.method == 'GET':
            try:
                forward_resp = requests.get(f'http://{forward_add}/key-value-store/{key}')
            except:
                error_resp['message'] = 'Error in GET'
                return Response(json.dumps(error_resp), 503, mimetype='application/json')
            return Response(forward_resp.text, forward_resp.status_code, mimetype='application/json')
        elif request.method == 'PUT':
            #app.logger.info(req_json)
            try:
                forward_resp = requests.put(f'http://{forward_add}/key-value-store/{key}', json = request.get_json())
            except:
                error_resp['message'] = 'Error in PUT'
                return Response(json.dumps(error_resp), 503, mimetype='application/json')
            # print(forward_resp)
            return Response(forward_resp.text, forward_resp.status_code, mimetype='application/json')
        elif request.method == 'DELETE':
            try:
                forward_resp = requests.delete(f'http://{forward_add}/key-value-store/{key}')
            except:
                error_resp['message'] = 'Error in DELETE'
                return Response(json.dumps(error_resp), 503, mimetype='application/json')
            # print(forward_resp)
            return Response(forward_resp.text, forward_resp.status_code, mimetype='application/json')
        return 'This method is unsupported.'


# Main Code to run
if __name__ == "__main__":
    app.run(host = '0.0.0.0', port = 8085, debug = True)
