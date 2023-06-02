from app import app
from model.users_model import users
from model.auth_model import auth_model
from flask import request, make_response
import traceback

from datetime import datetime


obj = users()
auth = auth_model()

@app.route("/user/login", methods=["POST"])
def user_login():
    try:
        return obj.user_login(request.data)
    except Exception as e:
        traceback.print_exc()
        return make_response(f"Error user_login controller : {e}", 204)
    
@app.route("/search_user_by_username", methods=["GET"])
@auth.token_auth()
def search_user_by_username():
    try:
        return obj.search_user_by_username(request.data)
    except Exception as e:
        traceback.print_exc()
        return make_response(f"error in search user by username controller: {e}", 204)
    
@app.route("/users", methods=["GET"])
# @auth.token_auth()
def get_all_users():
    try:
        return obj.get_all_users()
    except Exception as e:
        traceback.print_exc()
        return make_response(f"error in get all users controller: {e}", 204)
    
@app.route("/users", methods=["POST"])
# @auth.token_auth()
def add_user():
    try:
        return obj.add_user(request.data)
    except Exception as e:
        traceback.print_exc()
        return make_response(f"error in add user controller: {e}", 204)
    
@app.route("/user/<int:id>", methods=["GET"])
@auth.token_auth()
def get_user(id):
    try:
        return obj.get_user(id)
    except Exception as e:
        traceback.print_exc()
        return make_response(f"error in get user controller: {e}", 204)
    
@app.route("/user/<int:id>", methods=["PUT"])
@auth.token_auth()
def update_user(id):
    try:
        return obj.update_user(id, request.data)
    except Exception as e:
        traceback.print_exc()
        return make_response(f"error in update user controller: {e}", 204)
    
@app.route("/user/<int:id>", methods=["DELETE"])
@auth.token_auth()
def delete_user(id):
    try:
        return obj.delete_user(id)
    except Exception as e:
        traceback.print_exc()
        return make_response(f"error in delete user controller: {e}", 204)
    
@app.route("/user/ban/<int:id>", methods=["PUT"])
@auth.token_auth()
def ban_user(id):
    try:
        return obj.ban_user(id)
    except Exception as e:
        traceback.print_exc()
        return make_response(f"error in ban user controller: {e}", 204)
    
@app.route("/banned_users", methods=["GET"])
@auth.token_auth()
def get_all_banned_users():
    try:
        return obj.get_all_banned_users()
    except Exception as e:
        traceback.print_exc()
        return make_response(f"error in get all banned users controller: {e}", 204)


