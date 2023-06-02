from app import app
from model.auth_model import auth_model
from model.users_roles_model import users_roles
from flask import make_response, request
import traceback

import json

obj = users_roles()
auth = auth_model()


@app.route("/users_roles", methods=["GET"])
# @auth.token_auth()
def get_all_users_roles():
    try:
        return obj.get_all_users_roles()
    except Exception as e:
        traceback.print_exc()
        return make_response(f"error in getAll users roles controller: {e}", 204)


@app.route("/users_roles/<int:user_id>", methods=["GET"])
# @auth.token_auth()
def get_user_roles(user_id):
    try:
        return obj.get_user_roles(user_id)
    except Exception as e:
        traceback.print_exc()
        return make_response(f"error in get user roles controller: {e}", 204)


@app.route("/user_roles", methods=["POST"])
# @auth.token_auth()
def add_new_user_roles():
    try:
        return obj.add_new_user_roles(request.data)
    except Exception as e:
        traceback.print_exc()
        return make_response(f"Error in add new user roles controller : {e}", 204)
    
@app.route("/user_role", methods=["POST"])
# @auth.token_auth()
def add_new_user_role():
    try:
        return obj.add_new_user_role(request.data)
    except Exception as e:
        traceback.print_exc()
        return make_response(f"Error in add new user role controller : {e}", 204)


@app.route("/users_roles/<int:user_id>", methods=["DELETE"])
# @auth.token_auth()
def delete_user_roles(user_id):
    try:
        return obj.delete_user_roles(user_id)
    except Exception as e:
        return make_response(f"Error in deleting users_roles controller : {e}", 204)

@app.route("/users_roles/<int:user_id>", methods=["PUT"])
# @auth.token_auth()
def update_role_user_relationship(user_id):
    try:
        data = request.get_json()  # Get the data from the request body
        data_str = json.dumps(data)  # Convert the data to a JSON string
        return obj.update_role_user_relationship(user_id, data_str)  # Pass the JSON string to the method
    except Exception as e:
        return make_response(f"Error in updating user roles: {e}", 500)
