from app import app
from model.roles_model import roles
from model.auth_model import auth_model
from flask import request, make_response
import traceback
from flask import request, make_response
from flask_jwt_extended import jwt_required


obj = roles()
auth = auth_model()

@app.route("/search_by_role_name", methods=["GET"])
# @auth.token_auth()
def search_by_role_name():
    try:
        return obj.search_by_role_name(request.data)
    except Exception as e:
        traceback.print_exc()
        return make_response(f"error in search by role name controller: {e}", 204)
        

# obj = roles()
# auth = auth_model()

# @app.route("/search_by_role_name", methods=["GET"])
# @jwt_required() # protect the endpoint with JWT authentication
# def search_by_role_name():
#     search_term = request.args.get('search', '') # get the search term from the query parameter
#     try:
#         return obj.search_by_role_name(search_term)
#     except Exception as e:
#         traceback.print_exc()
#         return make_response(f"error in search by role name controller: {e}", 204)

    
@app.route("/roles", methods=["GET"])
# @auth.token_auth()
def get_all_roles():
    try:
        return obj.get_all_roles()
    except Exception as e:
        traceback.print_exc()
        return make_response(f"error in getAll roles controller: {e}", 204)

@app.route("/roles", methods=["POST"])
# @auth.token_auth()
def add_role():
    try:
        return obj.add_role(request.data)
    except Exception as e:
        traceback.print_exc()
        return make_response(f"error in add role controller: {e}", 204)
    
@app.route("/role/<int:id>", methods=["GET"])
# @auth.token_auth()
def get_role(id):
    try:
        return obj.get_role(id)
    except Exception as e:
        traceback.print_exc()
        return make_response(f"error in get role controller: {e}", 204)
    
@app.route("/role/<int:id>", methods=["PUT"])
# @auth.token_auth()
def update_role(id):
    try:
        return obj.update_role(id, request.data)
    except Exception as e:
        traceback.print_exc()
        return make_response(f"error in update role controller: {e}", 204)
    
@app.route("/role/<int:id>", methods=["DELETE"])
# @auth.token_auth()
def delete_role(id):
    try:
        return obj.delete_role(id)
    except Exception as e:
        traceback.print_exc()
        return make_response(f"error in delete role controller: {e}", 204)
    
# @app.route("/role/patch/<int:id>", methods=["PATCH"])
# @auth.token_auth()
# def patch_role(id):
#     try:
#         return obj.patch_role(request.data, id)
#     except Exception as e :
#         traceback.print_exc()
#         return make_response(f"Error in patch role controller : {e}", 204)

