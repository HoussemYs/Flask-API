from app import app
from model.profiles_model import profiles
from model.auth_model import auth_model
from flask import request, make_response, send_file
import traceback
from datetime import datetime
import os


obj = profiles()
auth = auth_model()

@app.route("/profiles/search", methods=["GET"])
# @auth.token_auth()
def search_profiles():
    try:
        term = request.args.get("term")
        if not term:
            return make_response({"message": "No search term provided"}, 400)
        results = obj.search_profiles(term)
        return results
    except Exception as e:
        traceback.print_exc()
        return make_response(f"Error in search profiles controller: {e}", 500)


@app.route("/profiles", methods=["GET"])
@auth.token_auth()
def get_all_profiles():
    try:
        return obj.get_all_profiles()
    except Exception as e:
        traceback.print_exc()
        return make_response(f"error in getAll profiles controller: {e}", 204)

@app.route("/profiles", methods=["POST"])
@auth.token_auth()
def add_profile():
    try:
        return obj.add_profile(request.data)
    except Exception as e:
        traceback.print_exc()
        return make_response(f"error in add profile controller: {e}", 204)
    

@app.route("/profile/<int:id>", methods=["GET"])
@auth.token_auth()
def get_profile(id):
    try:
        return obj.get_profile(id)
    except Exception as e:
        traceback.print_exc()
        return make_response(f"error in get profile controller: {e}", 204)

@app.route("/profile/by/user/id/<int:id>", methods=["GET"])
@auth.token_auth()
def getProfileByUserId(id):
    try:
        return obj.getProfileByUserId(id)
    except Exception as e:
        traceback.print_exc()
        return make_response(f"error in get profile controller: {e}", 204)
    
@app.route("/profile/<int:id>", methods=["PUT"])
@auth.token_auth()
def update_profile(id):
    try:
        return obj.update_profile(id, request.data)
    except Exception as e:
        traceback.print_exc()
        return make_response(f"error in update profile controller: {e}", 204)
    
@app.route("/profile/<int:id>", methods=["DELETE"])
@auth.token_auth()
def delete_profile(id):
    try:
        return obj.delete_profile(id)
    except Exception as e:
        traceback.print_exc()
        return make_response(f"error in delete profile controller: {e}", 204)

@app.route("/profile/upload/image/<int:uid>", methods=["PUT"])
# @auth.token_auth()
def profile_upload_image(uid):
    try:
        file = request.files['image']
        uniqueFileName = str(datetime.now().timestamp()).replace(".", "")
        fileNameSplit = file.filename.split(".")
        ext = fileNameSplit[len(fileNameSplit)-1]
        finalFilePath = f"uploads/images/{uniqueFileName}.{ext}"
        file.save(finalFilePath)
        return obj.profile_upload_image(uid, finalFilePath)
    except Exception as e :
        traceback.print_exc()
        return make_response(f"Error in upload profile image controller : {e}", 204)

@app.route("/image/<filename>", methods=["GET"])
# @auth.token_auth()
def profile_get_image(filename):
    try:
        return make_response(send_file(f"{os.getcwd()}/uploads/images/{filename}"), 200)
    except Exception as e :
        traceback.print_exc()
        return make_response(f"Error in get profile image controller : {e}", 204)
 
@app.route("/image/<int:id>", methods=["GET"])
# @auth.token_auth()
def get_image_by_id_profile(id):
    try:
        return send_file(obj.get_image_by_id_profile(id))
    except Exception as e :
        traceback.print_exc()
        return make_response(f"Error in get image by id profile controller : {e}", 204)
