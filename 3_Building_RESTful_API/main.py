from google.cloud import datastore
from flask import Flask, request
import json
import constants

app = Flask(__name__)
client = datastore.Client()


@app.route('/')
def index():
    return "Please navigate to /boats or /slips to use this API"\

# boats template


@app.route('/boats', methods=['POST', 'GET'])
def boats_get_post():
    if request.method == 'POST':
        content = request.get_json()
        # https://stackoverflow.com/questions/21985024/check-exist-post-value-in-python-Flask
        # https://www.programcreek.com/python/example/51515/flask.Response
        # https://stackoverflow.com/questions/25860304/how-do-i-set-response-headers-in-flask
        # https://stackoverflow.com/questions/11832639/how-to-specify-python-requests-http-put-body
        errObj = {"Error": "The request object is missing at least one of the required attributes"}
        if "name" not in content:
            return (json.dumps(errObj), 400)
        elif "type" not in content:
            return (json.dumps(errObj), 400)
        elif "length" not in content:
            return (json.dumps(errObj), 400)
        else:
            new_boat = datastore.entity.Entity(key=client.key(constants.boats))
            new_boat.update({"name": content["name"], "type": content["type"], "length": content["length"]})
            client.put(new_boat)
            new_boat["id"] = new_boat.key.id
            new_boat["self"] = str(request.base_url) + "/" + str(new_boat.key.id)
            return (json.dumps(new_boat), 201)
    elif request.method == 'GET':
        query = client.query(kind=constants.boats)
        results = list(query.fetch())
        for e in results:
            e["id"] = e.key.id
        return json.dumps(results)
    else:
        return 'Method not recognized'


@app.route('/boats/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def boats_put_delete(id):
    if request.method == 'GET':
        boat_key = client.key(constants.boats, int(id))
        boat = client.get(boat_key)
        errObj = {"Error": "No boat with this boat_id exists"}
        if boat is None:
            return (json.dumps(errObj), 404)
        else:
            boat["id"] = boat.key.id
            boat["self"] = str(request.base_url)
            return (json.dumps(boat), 200)

    elif request.method == 'PATCH':
        content = request.get_json()
        errObj = {"Error": "The request object is missing at least one of the required attributes"}
        if "name" not in content:
            return (json.dumps(errObj), 400)
        elif "type" not in content:
            return (json.dumps(errObj), 400)
        elif "length" not in content:
            return (json.dumps(errObj), 400)
        else:
            boat_key = client.key(constants.boats, int(id))
            boat = client.get(boat_key)
            errObj = {"Error": "No boat with this boat_id exists"}
            if boat is None:
                return (json.dumps(errObj), 404)
            else:
                boat.update({"name": content["name"], "type": content["type"], "length": content["length"]})
                boat["id"] = boat.key.id
                boat["self"] = str(request.base_url)
                client.put(boat)
                return (json.dumps(boat), 200)

    elif request.method == 'DELETE':
        boat_key = client.key(constants.boats, int(id))
        boat = client.get(boat_key)
        errObj = {"Error": "No boat with this boat_id exists"}
        if boat is None:
            return (json.dumps(errObj), 404)
        else:
            query = client.query(kind=constants.slips)
            results = list(query.fetch())
            for slip in results:
                if slip["current_boat"] == id:
                    slip.update({"current_boat": None})
                    client.put(slip)
            client.delete(boat_key)
            return ('', 204)

    else:
        return 'Method not recognized'

# slips template


@app.route('/slips', methods=['POST', 'GET'])
def slips_get_post():
    if request.method == 'POST':
        content = request.get_json()
        # https://stackoverflow.com/questions/21985024/check-exist-post-value-in-python-Flask
        # https://www.programcreek.com/python/example/51515/flask.Response
        # https://stackoverflow.com/questions/25860304/how-do-i-set-response-headers-in-flask
        # https://stackoverflow.com/questions/11832639/how-to-specify-python-requests-http-put-body
        errObj = {"Error": "The request object is missing the required number"}
        if "number" not in content:
            return (json.dumps(errObj), 400)
        else:
            new_slip = datastore.entity.Entity(key=client.key(constants.slips))
            new_slip.update({"number": content["number"], "current_boat": None})
            client.put(new_slip)
            new_slip["id"] = new_slip.key.id
            new_slip["self"] = str(request.base_url) + "/" + str(new_slip.key.id)
            return (json.dumps(new_slip), 201)
    elif request.method == 'GET':
        query = client.query(kind=constants.slips)
        results = list(query.fetch())
        for e in results:
            e["id"] = e.key.id
        return json.dumps(results)
    else:
        return 'Method not recognized'


@app.route('/slips/<int:id>', methods=['GET', 'DELETE'])
def slips_put_delete(id):
    if request.method == 'GET':
        slip_key = client.key(constants.slips, int(id))
        slip = client.get(slip_key)
        errObj = {"Error": "No slip with this slip_id exists"}
        if slip is None:
            return (json.dumps(errObj), 404)
        slip["id"] = slip.key.id
        slip["self"] = str(request.base_url)
        return json.dumps(slip)
    elif request.method == 'DELETE':
        slip_key = client.key(constants.slips, int(id))
        slip = client.get(slip_key)
        errObj = {"Error": "No slip with this slip_id exists"}
        if slip is None:
            return (json.dumps(errObj), 404)
        client.delete(slip_key)
        return ('', 204)
    else:
        return 'Method not recognized'


@app.route('/slips/<int:slip_id>/<int:boat_id>', methods=['PUT'])
def add_boat_to_slip(slip_id, boat_id):
    boat_key = client.key(constants.boats, int(boat_id))
    boat = client.get(boat_key)
    errObj = {"Error": "The specified boat and/or slip don’t exist"}
    if boat is None:
        return (json.dumps(errObj), 404)
    slip_key = client.key(constants.slips, int(slip_id))
    slip = client.get(slip_key)
    if slip is None:
        return (json.dumps(errObj), 404)
    if slip["current_boat"] is not None:
        errObj = {"Error": "The slip is not empty"}
        return (json.dumps(errObj), 403)
    slip.update({"current_boat": int(boat_id)})
    client.put(slip)
    return (json.dumps(slip), 204)


@app.route('/slips/<slip_id>/<boat_id>', methods=['DELETE'])
def remove_boat_from_slip(slip_id, boat_id):
    boat_key = client.key(constants.boats, int(boat_id))
    boat = client.get(boat_key)
    errObj = {"Error": "No boat with this boat_id is at the slip with this slip_id"}
    if boat is None:
        return (json.dumps(errObj), 404)
    slip_key = client.key(constants.slips, int(slip_id))
    slip = client.get(slip_key)
    if slip is None:
        return (json.dumps(errObj), 404)
    if slip["current_boat"] != int(boat_id):
        return (json.dumps(errObj), 404)
    slip.update({"current_boat": None})
    client.put(slip)
    return (json.dumps(slip), 204)
