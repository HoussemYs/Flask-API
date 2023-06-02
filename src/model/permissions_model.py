from app import app
from flask import request, make_response
import psycopg2
from db.database import connect
from datetime import datetime
import json
import logging

class permissions():

    def __init__(self):
        try:
            self.conn, self.cur = connect()
        except psycopg2.Error as error:
            print(error)





    def get_all_permissions(self):
        try:
            self.cur.execute("SELECT * FROM permissions")
            self.conn.commit()
            permissions = [
                dict(id=row[0], endpoint=row[1], method=row[2], description=row[3],permission_names=row[4])
                for row in self.cur.fetchall()
            ]
            if permissions is not None:
                logging.info(f"Someone consulted all permissions at {datetime.now()}")
                response = make_response(permissions, 200)
                response.headers['Access-Control-Allow-Origin'] = "*"
                return response
            else:
                return make_response({"message":"No permissions found !"}, 202)
        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error retrieving get all permissions : {e}"}, 500)
     
     
     
     
     
        
    def get_permission(self, id):
        try:
            self.cur.execute("SELECT * FROM permissions WHERE id=%s", (id,))
            row = self.cur.fetchone()
            if row is not None:
                permission = dict(id=row[0], endpoint=row[1], method=row[2], description=row[3])
                logging.info(f"Someone consulted permission with id : [ {id} ] at {datetime.now()}")
                res = make_response(permission, 200)
                res.headers['Access-Control-Allow-Origin'] = "*"
                return res
            else:
                return make_response({"message":"No permission found !"}, 202)
        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error retrieving get permission : {e}"}, 500)
      
      
      
      
        
    def add_permission(self, data):
        try:
            data_str = data.decode('utf-8')
            data_dict = json.loads(data_str)

            new_endpoint = data_dict['endpoint']
            new_method = data_dict['method']
            new_description = data_dict['description']

            # Check if the endpoint and method already exist in the database
            sql = """SELECT id FROM permissions WHERE endpoint = %s AND method = %s"""
            self.cur.execute(sql, (new_endpoint, new_method))
            existing_permission = self.cur.fetchone()

            if existing_permission is not None:
                # If the endpoint and method already exist, return an error response
                return make_response({"message": "Permission already exists"}, 409)

            # Generate the permission_names value
            permission_names = new_endpoint + ' ' + new_method

            sql = """INSERT INTO permissions (endpoint, method, description, permission_names)
                    VALUES (%s, %s, %s, %s)"""
            self.cur.execute(sql, (new_endpoint, new_method, new_description, permission_names))
            self.conn.commit()
            self.cur.execute("SELECT currval(pg_get_serial_sequence('permissions', 'id'));")
            permission_id = self.cur.fetchone()[0]
            logging.info(f"The permission with id: [{permission_id}], endpoint: [{new_endpoint}], method: [{new_method}] has been added at {datetime.now()}")
            res = make_response({"message": f"Permission with the id: {permission_id} created successfully"}, 201)
            res.headers['Access-Control-Allow-Origin'] = "*"
            return res
        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error retrieving add permission: {e}"}, 500)


    def update_permission(self, id, data):
        try:
            data_str = data.decode('utf-8')
            data_dict = json.loads(data_str)

            current_endpoint = data_dict['endpoint']
            current_method = data_dict['method']
            current_description = data_dict['description']

            sql = """UPDATE permissions
                    SET endpoint=%s,
                        method=%s,
                        description=%s
                    WHERE id=%s"""
            self.cur.execute(sql, (current_endpoint, current_method, current_description, id))
            self.conn.commit()

            # Return the updated permission
            updated_permission = {
                "endpoint": current_endpoint,
                "method": current_method,
                "description": current_description
            }
            logging.info(f"The user with id : [ {id} ], endpoint : [ {current_endpoint} ], method : [ {current_method} ] has been modified at {datetime.now()}")
            res = make_response(updated_permission, 201)
            res.headers['Access-Control-Allow-Origin'] = "*"
            return res
        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error retrieving update permission : {e}"}, 500)
            
            
            
            
    def delete_permission(self, id):
        try:
            self.cur.execute(f"DELETE from permissions WHERE id=%s",(id,) )
            self.conn.commit()
            if self.cur.rowcount>0:
                logging.info(f"The permission with id : [ {id} ] has been deleted at {datetime.now()}")
                res = make_response(f"Permission with id {id} deleted Successfully", 200)
                res.headers['Access-Control-Allow-Origin'] = "*"
                return res 
            else:
                return make_response("Nothing Deleted", 202)
        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error retrieving delete permission : {e}"}, 500)
        
        
        
        
    # def patch_permission(self, data, id):
    #     try:
    #         query = "UPDATE permissions SET "
    #         for key in data:
    #             query += f"{key}='{data[key]}',"
    #         query = query[:-1] + f" WHERE id=%s"
    #         print(query)    
    #         self.cur.execute(query, (id,) )
    #         self.conn.commit()
    #         if self.cur.rowcount>0:
    #             return make_response({"message":"Permission Updated in patch model successfully !"}, 201)
    #         else:
    #             return make_response({"message":"Nothing to Updated in patch model"}, 202)
    #     except Exception as e:
    #         self.conn.rollback()
    #         return make_response({"message": f"Error retrieving patch permission : {e}"}, 500)