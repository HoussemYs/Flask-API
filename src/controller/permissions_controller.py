from app import app
from model.permissions_model import permissions
from model.auth_model import auth_model
from flask import request, make_response
import traceback


obj = permissions()
auth = auth_model()

@app.route("/permissions", methods=["GET"])
# @auth.token_auth()
def get_all_permissions():
    try:
        return obj.get_all_permissions()
    except Exception as e:
        traceback.print_exc()
        return make_response(f"error in get all permissions controller: {e}", 204)

@app.route("/permissions", methods=["POST"])
# @auth.token_auth()
def add_permission():
    try:
        return obj.add_permission(request.data)
    except Exception as e:
        traceback.print_exc()
        return make_response(f"error in add permission controller: {e}", 204)
    
@app.route("/permission/<int:id>", methods=["GET"])
# @auth.token_auth()
def get_permission(id):
    try:
        return obj.get_permission(id)
    except Exception as e:
        traceback.print_exc()
        return make_response(f"error in get permission controller: {e}", 204)
    
@app.route("/permission/<int:id>", methods=["PUT"])
# @auth.token_auth()
def update_permission(id):
    try:
        return obj.update_permission(id, request.data)
    except Exception as e:
        traceback.print_exc()
        return make_response(f"error in update permission controller: {e}", 204)
    
@app.route("/permission/<int:id>", methods=["DELETE"])
# @auth.token_auth()
def delete_permission(id):
    try:
        return obj.delete_permission(id)
    except Exception as e:
        traceback.print_exc()
        return make_response(f"error in delete permission controller: {e}", 204)
    
# @app.route("/permission/patch/<int:id>", methods=["PATCH"])
# @auth.token_auth()
# def patch_permission(id):
#     try:
#         return obj.patch_permission(request.data, id)
#     except Exception as e :
#         traceback.print_exc()
#         return make_response(f"Error in patch permission controller : {e}", 204)

