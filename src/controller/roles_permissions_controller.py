from app import app
from model.roles_permissions_model import roles_permissions
from model.auth_model import auth_model
from flask import make_response, request, json
import traceback

import json

obj = roles_permissions()
auth = auth_model()


@app.route("/roles_permissions", methods=["GET"])
# @auth.token_auth()
def get_all_roles_permissions():
    try:
        return obj.get_all_roles_permissions()
    except Exception as e:
        traceback.print_exc()
        return make_response(f"error in getAll roles permissions controller: {e}", 204)


@app.route("/roles_permissions/<int:role_id>", methods=["GET"])
# @auth.token_auth()
def get_roles_permissions(role_id):
    try:
        return obj.get_roles_permissions(role_id)
    except Exception as e:
        traceback.print_exc()
        return make_response(f"error in get role permissions controller: {e}", 204)

# **********************************************************************************

@app.route("/roles_permissions", methods=["POST"])
# @auth.token_auth()
def add_new_roles_permissions():
    try:
        return obj.add_new_roles_permissions(request.data)
    except Exception as e:
        traceback.print_exc()
        return make_response(f"Error in add new roles_permissions controller : {e}", 204)


@app.route("/role_allpermissions", methods=["POST"])
# @auth.token_auth()
def add_new_role_allpermissions():
    try:
        return obj.add_new_role_allpermissions(request.data)
    except Exception as e:
        traceback.print_exc()
        return make_response(f"Error in add new role_allpermissions controller : {e}", 204)


@app.route("/roles_permissions/<int:role_id>", methods=["DELETE"])
# @auth.token_auth()
def delete_roles_permissions(role_id):
    try:
        print(role_id)
        return obj.delete_roles_permissions(role_id)
    except Exception as e:
        return make_response(f"Error in deleting roles_permissions controller : {e}", 204)


@app.route("/roles_permissions/<int:role_id>", methods=["PUT"])
# @auth.token_auth()
def update_role_permissions(role_id):
    try:
        data = request.get_json()  # Get the data from the request body
        data_str = json.dumps(data)  # Convert the data to a JSON string
        return obj.update_role_permissions(role_id, data_str)  # Pass the role_id and data string to the method
    except Exception as e:
        return make_response(f"Error in updating role permissions controller: {e}", 204)
