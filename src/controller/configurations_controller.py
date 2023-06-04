from app import app
from model.configurations_model import configurations
from model.auth_model import auth_model
from flask import request, make_response, send_file
import traceback
from datetime import datetime

obj = configurations()
auth = auth_model()

@app.route("/configurations/file/<int:id>", methods=["GET"])
# @auth.token_auth()
def get_file_by_id_config(id):
    try:
        file_path = obj.get_file_by_id_configuration(id)
        if file_path:
            return send_file(file_path)
        else:
            return make_response({"message": "No file found for this configuration!"}, 404)
    except Exception as e:
        traceback.print_exc()
        return make_response(f"Error in get file by id configuration: {e}", 500)
    
@app.route("/configurations/search", methods=["GET"])
# @auth.token_auth()
def search_configurations():
    try:
        term = request.args.get("term")
        if not term:
            return make_response({"message": "No search term provided"}, 400)
        results = obj.search_configurations(term)
        return results
    except Exception as e:
        traceback.print_exc()
        return make_response(f"Error in search configurations controller: {e}", 500)

@app.route("/versions/search", methods=["GET"])
# @auth.token_auth()
def search_versions():
    try:
        term = request.args.get("term")
        if not term:
            return make_response({"message": "No search term provided"}, 400)
        results = obj.search_versions(term)
        return results
    except Exception as e:
        traceback.print_exc()
        return make_response(f"Error in search versions controller: {e}", 500)
    

@app.route("/configurations", methods=["GET"])
# @auth.token_auth()
def get_all_configurations():
    try:
        return obj.get_all_configurations()
    except Exception as e:
        traceback.print_exc()
        return make_response(f"error in getAll configurations controller: {e}", 204)
    
@app.route("/configuration/<int:id>", methods=["GET"])
@auth.token_auth()
def get_configuration(id):
    try:
        return obj.get_configuration(id)
    except Exception as e:
        traceback.print_exc()
        return make_response(f"error in get configuration controller: {e}", 204)

# @app.route("/configurations", methods=["POST"])
# # @auth.token_auth()
# def add_configuration():
#     try:
#         data = request.form.to_dict()
        
#         if 'value' in request.files:
#             file = request.files['value']
#             uniqueFileName = str(datetime.now().timestamp()).replace(".", "")
#             fileNameSplit = file.filename.split(".")
#             ext = fileNameSplit[-1]
#             finalFilePath = f"uploads/files/{uniqueFileName}.{ext}"
#             file.save(finalFilePath)
#             data['value'] = finalFilePath

#         return obj.add_configuration(data)
#     except Exception as e:
#         traceback.print_exc()
#         return make_response(f"error in add configuration controller: {e}", 500)

@app.route("/configurations", methods=["POST"])
def add_configuration():
    try:
        data = request.get_json()
        finalFilePath = None

        if 'value' in data:
            if request.files and 'value' in request.files:
                file = data['value']
                uniqueFileName = str(datetime.now().timestamp()).replace(".", "")
                fileNameSplit = file.filename.split(".")
                ext = fileNameSplit[-1]
                finalFilePath = f"uploads/files/{uniqueFileName}.{ext}"
                file.save(finalFilePath)
                data['value'] = finalFilePath
                # with open(finalFilePath, 'w') as file:
                #     file.write(file)

        return obj.add_configuration(data,finalFilePath)
    except Exception as e:
        traceback.print_exc()
        return make_response(f"error in add configuration controller: {e}", 500)



@app.route("/configuration/patch/<int:id>", methods=["PATCH"])
@auth.token_auth()
def patch_configuration(id):
    try:
        return obj.patch_configuration(id, request.form)
    except Exception as e:
        traceback.print_exc()
        return make_response(f"Error in patch configuration controller : {e}", 204)
    
@app.route("/configuration/<int:id>", methods=["PUT"])
@auth.token_auth()
def update_configuration(id):
    try:
        return obj.update_configuration(id, request.data, request)
    except Exception as e:
        traceback.print_exc()
        return make_response(f"error in update configuration controller: {e}", 204)

@app.route("/configuration/<int:id>", methods=["DELETE"])
# @auth.token_auth()
def delete_configuration(id):
    try:
        return obj.delete_configuration(id)
    except Exception as e:
        traceback.print_exc()
        return make_response(f"error in delete configuration controller: {e}", 204)



                                     # TABLE CONFIGURATION VERSION

@app.route("/versionner/<int:id>", methods=["put"])
# @auth.token_auth()
def versionner_configuration(id):
    try:
        data = request.form.to_dict()
        if 'value' in request.files:
            file = request.files['value']
            uniqueFileName = str(datetime.now().timestamp()).replace(".", "")
            fileNameSplit = file.filename.split(".")
            ext = fileNameSplit[-1]
            finalFilePath = f"uploads/files/{uniqueFileName}.{ext}"
            file.save(finalFilePath)
            # data['value'] = finalFilePath

        return obj.versionner_configuration(id, request.data, request, finalFilePath)
    except Exception as e:
        traceback.print_exc()
        return make_response(f"error in update configuration controller: {e}", 204)

@app.route("/rollback/<int:id>", methods=["get"])
@auth.token_auth()
def rollback_configuration(id):
    try:
        return obj.rollback_configuration(id)
    except Exception as e:
        traceback.print_exc()
        return make_response(f"error in get configuration controller: {e}", 204)


@app.route("/backup/<int:id>", methods=["get"])
@auth.token_auth()
def backup_configuration(id):
    try:
        return obj.backup_configuration(id)
    except Exception as e:
        traceback.print_exc()
        return make_response(f"error in get configuration controller: {e}", 204)

@app.route("/deleteversion/<int:id>", methods=["DELETE"])
@auth.token_auth()
def delete_configuration_version(id):
    try:
        return obj.delete_configuration_version(id)
    except Exception as e:
        traceback.print_exc()
        return make_response(f"error in get configuration controller: {e}", 204)


@app.route("/configurationsversion", methods=["Get"])
@auth.token_auth()
def get_all_configurations_versions():
    try:
        return obj.get_all_configurations_versions()
    except Exception as e:
        traceback.print_exc()
        return make_response(f"error in get configuration controller: {e}", 204)


@app.route("/configurationversion/<int:id>", methods=["GET"])
@auth.token_auth()
def get_configuration_version(id):
    try:
        return obj.get_configuration_version(id)
    except Exception as e:
        traceback.print_exc()
        return make_response(f"error in get configuration controller: {e}", 204)
    
