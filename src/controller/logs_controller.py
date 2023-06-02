from app import app
from model.auth_model import auth_model
from model.logs_model import logs
from flask import request, make_response
import traceback
from flask import session  # Assuming you are using Flask sessions
import jwt


obj = logs()
auth = auth_model()


@app.route('/logs', methods=["GET"])
@auth.token_auth()
def get_logs():
    try:
        user_id = session.get('user_id')  # Retrieve the user ID from the session
        return obj.get_all_logs(user_id)
    except Exception as e:
        traceback.print_exc()
        return make_response(f"Error in get all logs controller: {e}", 204)

def extract_user_id_from_request(request):
    token = request.headers.get("Authorization", "").split(" ")[-1]
    if token:
        try:
            jwtdecoded = jwt.decode(token, "HoussemYousfi", algorithms="HS256")
            return jwtdecoded.get("user_id")
        except jwt.ExpiredSignatureError:
            return None
    return None

@app.route("/logs", methods=["POST"])
# @auth.token_auth()
def add_log():
    try:
        data = request.data
        user_id = extract_user_id_from_request(request)  # Extract the user ID from the request
        return obj.add_log(data, user_id)
    except Exception as e:
        traceback.print_exc()
        return make_response(f"error in add log controller: {e}", 204)
