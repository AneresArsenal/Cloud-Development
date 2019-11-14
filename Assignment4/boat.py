from flask import Blueprint, request
from google.cloud import datastore
import json
import constants

client = datastore.Client()

bp = Blueprint('boat', __name__, url_prefix='/boats')


@bp.route('', methods=['POST', 'GET'])
def boats_get_post():
    if request.method == 'POST':
        content = request.get_json()
        errObj = {"Error": "The request object is missing at least one of the required attributes"}
        if "name" not in content:
            return (json.dumps(errObj), 400)
        elif "type" not in content:
            return (json.dumps(errObj), 400)
        elif "length" not in content:
            return (json.dumps(errObj), 400)
        else:
            new_boat = datastore.entity.Entity(key=client.key(constants.boats))
            new_boat.update({"name": content["name"], "type": content["type"], "length": content["length"], "loads": [], "id": None, "self": None})
            client.put(new_boat)
            new_boat["id"] = new_boat.key.id
            new_boat["self"] = str(request.base_url) + "/" + str(new_boat.key.id)
            return (json.dumps(new_boat), 201)

    elif request.method == 'GET':
        query = client.query(kind=constants.boats)
        q_limit = int(request.args.get('limit', '3'))
        q_offset = int(request.args.get('offset', '0'))
        l_iterator = query.fetch(limit=q_limit, offset=q_offset)
        pages = l_iterator.pages
        results = list(next(pages))
        if l_iterator.next_page_token:
            next_offset = q_offset + q_limit
            next_url = request.base_url + "?limit=" + str(q_limit) + "&offset=" + str(next_offset)
        else:
            next_url = None
        for e in results:
            e["id"] = e.key.id
            e["self"] = str(request.base_url) + "/" + str(e.key.id)
        output = {"boats": results}
        if next_url:
            output["next"] = next_url
        return json.dumps(output)
    else:
        return 'Method not recognized'


@bp.route('/<id>', methods=['GET', 'PATCH', 'DELETE'])
def boats_patch_delete(id):
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
        boat_key = client.key(constants.boats, int(id))
        boat = client.get(key=boat_key)
        if boat is None:
            errObj = {"Error": "No boat with this boat_id exists"}
            return (json.dumps(errObj), 404)
        else:
            boat.update({"name": content["name"], "type": content["type"], "length": content["length"]})
            client.put(boat)
            boat["id"] = boat.key.id
            boat["self"] = str(request.base_url)
            return (json.dumps(boat), 200)
    elif request.method == 'DELETE':
        boat_key = client.key(constants.boats, int(id))
        boat = client.get(key=boat_key)
        errObj = {"Error": "No boat with this boat_id exists"}
        if boat is None:
            return (json.dumps(errObj), 404)
        else:
            if len(boat["loads"]) > 0:
                for each in boat["loads"]:
                    load_id = each["id"]
                    load_key = client.key(constants.loads, int(load_id))
                    load = client.get(key=load_key)
                    if load is not None:
                        load["carrier"] = None
                        client.put(load)
                client.delete(boat_key)
                return ('', 204)
            else:
                client.delete(boat_key)
                return ('', 204)
    else:
        return 'Method not recognized'


# @bp.route('/<boat_id>/loads/<load_id>', methods=['PUT', 'DELETE'])
# def add_delete_reservation(boat_id, load_id):
#     if request.method == 'PUT':
#         boat_key = client.key(constants.boats, int(boat_id))
#         boat = client.get(key=boat_key)
#         load_key = client.key(constants.loads, int(load_id))
#         load = client.get(key=load_key)
#         if 'loads' in boat.keys():
#             boat['loads'].append(load.id)
#         else:
#             boat['loads'] = [load.id]
#         client.put(boat)
#         return('', 200)
#     if request.method == 'DELETE':
#         boat_key = client.key(constants.boats, int(boat_id))
#         boat = client.get(key=boat_key)
#         if 'loads' in boat.keys():
#             boat['loads'].remove(int(load_id))
#             client.put(boat)
#         return('', 200)


@bp.route('/<id>/loads', methods=['GET'])
def get_boat_loads(id):
    boat_key = client.key(constants.boats, int(id))
    boat = client.get(key=boat_key)
    if len(boat["loads"]) > 0:
        return json.dumps(boat["loads"])
    else:
        return json.dumps([])
