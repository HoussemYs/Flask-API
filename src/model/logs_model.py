
from app import app
from flask import request, make_response, json
import psycopg2
from datetime import datetime, timedelta
import jwt
from db.database import connect
import json
import logging
from flask import session  # Assuming you are using Flask sessions


class logs():
    def __init__(self):
        try:
            self.conn, self.cur = connect()
        except psycopg2.Error as error:
            print(error)



    def get_all_logs(self, user_id):
        def extract_user_id_from_request():
            token = request.headers.get("Authorization", "").split(" ")[-1]
            if token:
                try:
                    jwtdecoded = jwt.decode(token, "HoussemYousfi", algorithms="HS256")
                    return jwtdecoded.get("user_id"), jwtdecoded.get("role_id")
                except jwt.ExpiredSignatureError:
                    return None, None
            return None, None

        try:
            token_user_id, token_role_id = extract_user_id_from_request()
            if token_user_id is None or token_role_id is None:
                return make_response({"message": "Invalid token!"}, 401)

            if 81 in token_role_id:
                self.cur.execute("SELECT * FROM logs")
            else:
                self.cur.execute(f"SELECT * FROM logs WHERE id_user = '{token_user_id}'")
            
            self.conn.commit()
            logs = [
                dict(id=row[0], action=row[1], date=row[2], id_user=row[3])  # Add id_user to the dict
                for row in self.cur.fetchall()
            ]
            
            if logs:
                return make_response(logs, 200)
            else:
                return make_response({"message": "No logs found!"}, 202)
        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error retrieving all logs: {e}"}, 500)

    # def add_log(self, data):
    #     try:
    #         data_str = data.decode('utf-8')
    #         data_dict = json.loads(data_str)

    #         action = data_dict['action']
    #         sql = """INSERT INTO logs (action, date)
    #                 VALUES (%s, %s)"""
    #         self.cur.execute(sql, (action, datetime.now()))
    #         self.conn.commit()
    #         self.cur.execute("SELECT currval(pg_get_serial_sequence('logs', 'id'));")
    #         log_id = self.cur.fetchone()[0] 
    #         res = make_response({"message": f"created successfully"}, 201)
    #         res.headers['Access-Control-Allow-Origin'] = "*"
    #         return res
    #     except KeyError as e:
    #         self.conn.rollback()
    #         return make_response({"message": f"Error: Missing required parameter '{e.args[0]}'"}, 400)
    #     except Exception as e:
    #         self.conn.rollback()
    #         return make_response({"message": f"Error creating logs: {e}"}, 500)
 
 
    def add_log(self, data, user_id):
        try:
            data_str = data.decode('utf-8')
            data_dict = json.loads(data_str)

            action = data_dict['action']
            sql = """INSERT INTO logs (action, date, id_user)
                    VALUES (%s, %s, %s)"""
            self.cur.execute(sql, (action, datetime.now(), user_id))
            self.conn.commit()
            
            log_id = self.cur.lastrowid  # Retrieve the ID of the last inserted row
            res = make_response({"message": f"created successfully", "log_id": log_id}, 201)
            res.headers['Access-Control-Allow-Origin'] = "*"
            return res
        except KeyError as e:
            self.conn.rollback()
            return make_response({"message": f"Error: Missing required parameter '{e.args[0]}'"}, 400)
        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error creating logs: {e}"}, 500)




    # def add_log(self, data, user_id):
    #     try:
    #         data_str = data.decode('utf-8')
    #         data_dict = json.loads(data_str)
    #         action = data_dict['action']
    #         sql = """INSERT INTO logs (action, date, id_user)
    #                 VALUES (%s, %s, %s)"""
    #         self.cur.execute(sql, (action, datetime.now(), user_id))
    #         self.conn.commit()
    #         res = make_response({"message": "Created successfully"}, 201)
    #         res.headers['Access-Control-Allow-Origin'] = "*"
    #         return res
    #     except KeyError as e:
    #         self.conn.rollback()
    #         return make_response({"message": f"Error: Missing required parameter '{e.args[0]}'"}, 400)
    #     except Exception as e:
    #         self.conn.rollback()
    #         return make_response({"message": f"Error creating logs: {e}"}, 500)
