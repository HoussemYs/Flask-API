#Code Description:
    # Function token_auth : Verif if the current user has the permission for access to the api requested or not !



from functools import wraps
import psycopg2
from app import app
from urllib import request
from flask import make_response, request, json, session
import jwt
import re
from db.database import connect


class auth_model():
    def __init__(self):
        try:
            self.conn, self.cur = connect()
        except psycopg2.Error as error:
            print(error)

    # def token_auth(self, endpoint=""):
    #     def inner1(func):
    #         @wraps(func)
    #         def inner2(*args, **kwargs):
    #             endpoint = request.url_rule.rule

    #             # Check if user is logged in using session-based authentication
    #             if 'user_info' in session:
    #                 user_info = session['user_info']
                    
    #                 # Retrieve the user's role_ids from the session
    #                 role_ids = user_info.get("role_ids", [])

    #                 # Verify user roles and permissions as before
    #                 self.cur.execute(f"SELECT id FROM permissions WHERE endpoint = '{endpoint}' AND method = '{request.method}'")
    #                 permission = self.cur.fetchone()
    #                 if permission is None:
    #                     return make_response({"ERROR": "INVALID_PERMISSION CHECK YOUR REQUEST API"}, 401)
    #                 per_id = permission[0]
    #                 self.cur.execute(f"SELECT role_id FROM roles_permissions WHERE permission_id= '{per_id}'")
    #                 result = self.cur.fetchall()
    #                 if result is not None:
    #                     role_ids_db = [res[0] for res in result]
    #                     if set(role_ids).intersection(set(role_ids_db)):
    #                         return func(*args, **kwargs)
    #                     else:
    #                         return make_response({"ERROR": "INVALID_ROLE TRY WITH ANOTHER ACCOUNT OR ADD THE CORRECT ROLE TO THIS USER"}, 403)
    #                 else:
    #                     return make_response({"ERROR": "UNKNOWN_ENDPOINT"}, 404)

    #             # Check if user is logged in using JWT Bearer token
    #             token = request.headers.get("Authorization", "").split(" ")[-1]
    #             if token:
    #                 try:
    #                     jwtdecoded = jwt.decode(token, "HoussemYousfi", algorithms="HS256")
    #                     user_info = {
    #                         "user_id": jwtdecoded["user_id"],
    #                         "username": jwtdecoded["username"],
    #                         "password": jwtdecoded["password"],
    #                         "type_id": jwtdecoded["type_id"],
    #                         "role_ids": jwtdecoded.get("role_id", [])
    #                     }
                        
    #                     role_ids = user_info.get("role_ids", [])
    #                     if not role_ids:
    #                         return make_response({"ERROR": "USER_HAS_NO_ROLES"}, 401)
                        
    #                     self.cur.execute(f"SELECT id FROM permissions WHERE endpoint = '{endpoint}' AND method = '{request.method}'")
    #                     permission = self.cur.fetchone()
    #                     if permission is None:
    #                         return make_response({"ERROR": "INVALID_PERMISSION CHECK YOUR REQUEST API"}, 401)
    #                     per_id = permission[0]
    #                     self.cur.execute(f"SELECT role_id FROM roles_permissions WHERE permission_id= '{per_id}'")
    #                     result = self.cur.fetchall()
    #                     if result is not None:
    #                         role_ids_db = [res[0] for res in result]
    #                         if set(role_ids).intersection(set(role_ids_db)):
    #                             return func(*args, **kwargs)
    #                         else:
    #                             return make_response({"ERROR": "INVALID_ROLE TRY WITH ANOTHER ACCOUNT OR ADD THE CORRECT ROLE TO THIS USER"}, 403)
    #                     else:
    #                         return make_response({"ERROR": "UNKNOWN_ENDPOINT"}, 404)
    #                 except jwt.ExpiredSignatureError:
    #                     return make_response({"ERROR": "TOKEN_EXPIRED! RECONNECT"}, 401)
    #             else:
    #                 return make_response({"ERROR": "INVALID_TOKEN PLEASE SEND THE CORRECT TOKEN WITH CORRECT FORMAT"}, 401)
    #         return inner2
    #     return inner1



    def token_auth(self, endpoint=""):
        def inner1(func):
            @wraps(func)
            def inner2(*args, **kwargs):
                endpoint = request.url_rule.rule
                # print(endpoint)
                token = request.headers.get("Authorization", "").split(" ")[-1]
                # print(token)
                if token:
                    try:
                        jwtdecoded = jwt.decode(token, "HoussemYousfi", algorithms="HS256")
                        user_info = {
                            "user_id": jwtdecoded["user_id"],
                            "username": jwtdecoded["username"],
                            "password": jwtdecoded["password"],
                            "type_id": jwtdecoded["type_id"],
                            "role_ids": jwtdecoded.get("role_id", [])
                        }
                        
                        # print(user_info)
                    except jwt.ExpiredSignatureError:
                        return make_response({"ERROR": "TOKEN_EXPIRED! RECONNECT"}, 401)
                    
                    role_ids = user_info.get("role_ids", [])
                    if not role_ids:
                        return make_response({"ERROR": "USER_HAS_NO_ROLES"}, 401)
                    
                    self.cur.execute(f"SELECT id FROM permissions WHERE endpoint = '{endpoint}' AND method = '{request.method}'")
                    permission = self.cur.fetchone()
                    if permission is None:
                        return make_response({"ERROR": "INVALID_PERMISSION CHECK YOUR REQUEST API"}, 401)
                    per_id = permission[0]
                    self.cur.execute(f"SELECT role_id FROM roles_permissions WHERE permission_id= '{per_id}'")
                    result = self.cur.fetchall()
                    if result is not None:
                        role_ids_db = [res[0] for res in result]
                        # if role_id in role_ids_db:
                        if set(role_ids).intersection(set(role_ids_db)):
                            return func(*args, **kwargs)
                        else:
                            return make_response({"ERROR": "INVALID_ROLE TRY WITH ANOTHER ACCOUNT OR ADD THE CORRECT ROLE TO THIS USER"}, 403)
                    else:
                        return make_response({"ERROR": "UNKNOWN_ENDPOINT"}, 404)
                else:
                    return make_response({"ERROR": "INVALID_TOKEN PLEASE SEND THE CORRECT TOKEN WITH CORRECT FORMAT"}, 401)
            return inner2
        return inner1
    