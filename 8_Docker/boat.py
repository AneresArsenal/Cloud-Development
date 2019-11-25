from flask import Blueprint, request, jsonify, render_template_string
from google.cloud import datastore
import json
import constants


client = datastore.Client()

bp = Blueprint('boat', __name__, url_prefix='/boats')


@bp.route('', methods=['POST', 'GET', 'PATCH', 'PUT', 'DELETE'])
def boats_post():
    if request.method == 'POST':
        if not request.is_json:
            errObj = {"Error": "Content-Type is not JSON"}
            return (jsonify(errObj), 406)
        content = request.get_json()
        query = client.query(kind=constants.boats)
        results = list(query.fetch())
        for e in results:
            if e["name"] == content["name"]:
                errObj = {"Error": "Boat name already exists"}
                return (jsonify(errObj), 403)
        errObj = {"Error": "The request object is missing at least one of the required attributes or is of an invalid data type"}
        if "name" not in content or type(content["name"]) is not str:
            return (jsonify(errObj), 400)
        if "type" not in content or type(content["type"]) is not str:
            return (jsonify(errObj), 400)
        if "length" not in content or type(content["length"]) is not int:
            return (jsonify(errObj), 400)
        # reference: https://stackoverflow.com/questions/29454773/how-can-i-tell-if-a-string-only-contains-letter-and-spaces
        if all(x.isalnum() or x.isspace() for x in content["name"]) and all(x.isalnum() or x.isspace() for x in content["type"]):
            content = request.get_json()
            new_boat = datastore.entity.Entity(key=client.key(constants.boats))
            new_boat.update({"name": content["name"], "type": content["type"], "length": content["length"]})
            client.put(new_boat)
            new_boat["id"] = new_boat.key.id
            new_boat["self"] = str(request.base_url) + "/" + str(new_boat.key.id)
            return (jsonify(new_boat), 201)
        else:
            errObj = {"Error": "Only alphanumeric characters allowed for name and type attributes"}
            return (jsonify(errObj), 400)

    elif request.method == 'GET':
        query = client.query(kind=constants.boats)
        results = list(query.fetch())
        for e in results:
            e["id"] = e.key.id
        return jsonify(results)

    else:
        errObj = {"Error": "Method Not Allowed"}
        return (jsonify(errObj), 405)


@bp.route('/<id>', methods=['GET', 'PATCH', 'PUT', 'DELETE'])
def boats_patch_put(id):
    if request.method == 'GET':
        boat_key = client.key(constants.boats, int(id))
        boat = client.get(boat_key)
        errObj = {"Error": "No boat with this boat_id exists"}
        if boat is None:
            return (jsonify(errObj), 404)
        else:
            boat["id"] = boat.key.id
            boat["self"] = str(request.base_url)
            # if 'application/json' in request.accept_mimetypes:
            return (jsonify(boat), 200)
#             elif 'text/html' in request.accept_mimetypes:
#                 # return (json.dumps(boat), 200)
#                 return render_template_string('''
#     <table>
#             <tr>
#                 <td> Attribute: Content </td>
#             </tr>
#     {% for key, value in labels.items() %}
#             <tr>
#                 <td> {{ key }}: {{ value }} </td>
#             </tr>
#     {% endfor %}
#     </table>
# ''', labels=boat)
#             else:
#                 errObj = {"Error": "Invalid format requested"}
#                 return (jsonify(errObj), 406)

    elif request.method == 'PATCH' or request.method == 'PUT':
        if not request.is_json:
            errObj = {"Error": "Content-Type is not JSON"}
            return (jsonify(errObj), 406)
        content = request.get_json()
        if "id" in content:
            errObj = {"Error": "Updating the value of id is not allowed"}
            return (jsonify(errObj), 403)

        query = client.query(kind=constants.boats)
        results = list(query.fetch())
        for e in results:
            if e["name"] == content["name"] and e.key.id != int(id):
                errObj = {"Error": "Boat name already exists"}
                return (jsonify(errObj), 403)

        if request.method == 'PATCH':
            boat_key = client.key(constants.boats, int(id))
            boat = client.get(key=boat_key)
            if boat is None:
                errObj = {"Error": "No boat with this boat_id exists"}
                return (jsonify(errObj), 404)
            errObj = {"Error": "One of the attribute requested content provided is of an invalid data type"}
            if "name" in content:
                if type(content["name"]) is not str:
                    return (jsonify(errObj), 400)
                elif all(x.isalnum() or x.isspace() for x in content["name"]):
                    boat.update({"name": content["name"]})
                else:
                    errObj = {"Error": "Only alphanumeric characters allowed for name and type attributes"}
                    return (jsonify(errObj), 400)
            if "type" in content:
                if type(content["type"]) is not str:
                    return (jsonify(errObj), 400)
                elif all(x.isalnum() or x.isspace() for x in content["name"]):
                    boat.update({"type": content["type"]})
                else:
                    errObj = {"Error": "Only alphanumeric characters allowed for name and type attributes"}
                    return (jsonify(errObj), 400)
            if "length" in content:
                if type(content["length"]) is not int:
                    return (jsonify(errObj), 400)
                else:
                    boat.update({"length": content["length"]})
            client.put(boat)
            boat["id"] = boat.key.id
            boat["self"] = str(request.base_url)
            return (jsonify(boat), 200)

        else:
            errObj = {"Error": "The request object is missing at least one of the required attributes or is of an invalid data type"}
            if "name" not in content or type(content["name"]) is not str:
                return (jsonify(errObj), 400)
            if "type" not in content or type(content["type"]) is not str:
                return (jsonify(errObj), 400)
            if "length" not in content or type(content["length"]) is not int:
                return (jsonify(errObj), 400)
            boat_key = client.key(constants.boats, int(id))
            boat = client.get(key=boat_key)
            if boat is None:
                errObj = {"Error": "No boat with this boat_id exists"}
                return (jsonify(errObj), 404)
            elif all(x.isalnum() or x.isspace() for x in content["name"]) and all(x.isalnum() or x.isspace() for x in content["type"]):
                boat.update({"name": content["name"], "type": content["type"], "length": content["length"]})
                client.put(boat)
                boat["id"] = boat.key.id
                boat["self"] = str(request.base_url)
                return (jsonify(boat), 303)
            else:
                errObj = {"Error": "Only alphanumeric characters allowed for name and type attributes"}
                return (jsonify(errObj), 400)

    elif request.method == 'DELETE':
        boat_key = client.key(constants.boats, int(id))
        boat = client.get(key=boat_key)
        errObj = {"Error": "No boat with this boat_id exists"}
        if boat is None:
            return (jsonify(errObj), 404)
        else:
            client.delete(boat_key)
            return ('', 204)

    else:
        return 'Method not recognized'
