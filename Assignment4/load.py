from flask import Blueprint, request
from google.cloud import datastore
import json
import constants
from urllib.parse import urlparse

client = datastore.Client()

bp = Blueprint('load', __name__, url_prefix='/loads')


@bp.route('', methods=['POST', 'GET'])
def loads_get_post():
    if request.method == 'POST':
        content = request.get_json()
        errObj = {"Error": "The request object is missing at least one of the required attributes"}
        if "weight" not in content:
            return (json.dumps(errObj), 400)
        elif "content" not in content:
            return (json.dumps(errObj), 400)
        elif "delivery_date" not in content:
            return (json.dumps(errObj), 400)
        new_load = datastore.entity.Entity(key=client.key(constants.loads))
        new_load.update({"weight": content["weight"], "content": content["content"], "carrier": None, "delivery_date": content["delivery_date"]})
        client.put(new_load)
        new_load["id"] = new_load.key.id
        new_load["self"] = str(request.base_url) + "/" + str(new_load.key.id)
        return (json.dumps(new_load), 201)
    elif request.method == 'GET':
        query = client.query(kind=constants.loads)
        q_limit = int(request.args.get('limit', '3'))
        q_offset = int(request.args.get('offset', '0'))
        g_iterator = query.fetch(limit=q_limit, offset=q_offset)
        pages = g_iterator.pages
        results = list(next(pages))
        if g_iterator.next_page_token:
            next_offset = q_offset + q_limit
            next_url = request.base_url + "?limit=" + str(q_limit) + "&offset=" + str(next_offset)
        else:
            next_url = None
        for e in results:
            e["id"] = e.key.id
            e["self"] = str(request.base_url) + "/" + str(e.key.id)
        output = {"loads": results}
        if next_url:
            output["next"] = next_url
        return json.dumps(output)


@bp.route('/<id>', methods=['GET', 'PUT', 'DELETE'])
def loads_get_put_delete(id):
    if request.method == 'GET':
        load_key = client.key(constants.loads, int(id))
        load = client.get(load_key)
        errObj = {"Error": "No load with this load_id exists"}
        if load is None:
            return (json.dumps(errObj), 404)
        else:
            load["id"] = load.key.id
            load["self"] = str(request.base_url)
            return (json.dumps(load), 200)
    elif request.method == 'PUT':
        content = request.get_json()
        load_key = client.key(constants.loads, int(id))
        load = client.get(key=load_key)
        load.update({"name": content["name"]})
        client.put(load)
        return (json.dumps(load), 204)
    elif request.method == 'DELETE':
        load_key = client.key(constants.loads, int(id))
        load = client.get(key=load_key)
        errObj = {"Error": "No load with this load_id exists"}
        if load is None:
            return (json.dumps(errObj), 404)
        else:
            if load["carrier"] is None:
                client.delete(load_key)
                return ('', 204)
            else:
                boat_id = load["carrier"]["id"]
                boat_key = client.key(constants.boats, int(boat_id))
                boat = client.get(key=boat_key)
                if boat is not None:
                    if boat["loads"] is not None:
                        for each in boat["loads"]:
                            if int(each["id"]) == int(id):
                                boat["loads"].remove(each)
                                client.put(boat)
                client.delete(load_key)
                return ('', 204)
    else:
        return 'Method not recognized'


@bp.route('/<load_id>/boats/<boat_id>', methods=['GET', 'PUT', 'DELETE'])
def loads_boat_get_put_delete(load_id, boat_id):
    if request.method == 'GET':
        load_key = client.key(constants.loads, int(load_id))
        load = client.get(load_key)
        errObj = {"Error": "No load with this load_id exists"}
        if load is None:
            return (json.dumps(errObj), 404)
        else:
            load["id"] = load.key.id
            load["self"] = str(request.base_url)
            return (json.dumps(load), 200)
    elif request.method == 'PUT':
        load_key = client.key(constants.loads, int(load_id))
        load = client.get(key=load_key)
        boat_key = client.key(constants.boats, int(boat_id))
        boat = client.get(key=boat_key)
        errObj = {"Error": "The specified boat and or slip do not exist"}
        if load is None or boat is None:
            return (json.dumps(errObj), 404)
        elif load["carrier"] is None:
            # source: https://stackoverflow.com/questions/9626535/get-protocol-host-name-from-url
            parsed_uri = urlparse(str(request.base_url))
            boat_self = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
            boat_self = boat_self + "boats/" + str(boat.key.id)
            load.update({"carrier": {"id": boat_id, "name": boat["name"], "self": boat_self}})
            client.put(load)
            # source: https://stackoverflow.com/questions/9626535/get-protocol-host-name-from-url
            parsed_uri = urlparse(str(request.base_url))
            load_self = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
            load_self = load_self + "loads/" + str(load.key.id)
            boat["loads"].append({"id": load_id, "self": str(load_self)})
            client.put(boat)
            return (json.dumps(load), 204)
        else:
            errObj = {"Error": "Load currently has a carrier"}
            return (json.dumps(errObj), 403)
    elif request.method == 'DELETE':
        load_key = client.key(constants.loads, int(load_id))
        load = client.get(key=load_key)
        boat_key = client.key(constants.boats, int(boat_id))
        boat = client.get(key=boat_key)
        if load is None or boat is None:
            errObj = {"Error": "The specified boat and or slip do not exist"}
            return (json.dumps(errObj), 404)
        elif load["carrier"] is None:
            errObj = {"Error": "No boat is assigned the load."}
            return (json.dumps(errObj), 404)
        elif int(load["carrier"]["id"]) != int(boat.key.id):
            errObj = {"Error": "No boat with this boat_id is assigned the load with this load_id"}
            return (json.dumps(errObj), 404)
        else:
            for each in boat["loads"]:
                if int(each["id"]) == int(load_id):
                    boat["loads"].remove(each)
            client.put(boat)
            load.update({"carrier": None})
            client.put(load)
            return ('', 204)
    else:
        return 'Method not recognized'
