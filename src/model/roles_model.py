from app import app
from flask import request, make_response, json
import psycopg2
from db.database import connect
from datetime import datetime
import logging


class roles():

    def __init__(self):
        try:
            self.conn, self.cur = connect()
        except psycopg2.Error as error:
            print(error)




    def get_all_roles(self):
        try:
            self.cur.execute("SELECT * FROM roles")
            self.conn.commit()
            roles = [
                dict(id=row[0], name=row[1], description=row[2])
                for row in self.cur.fetchall()
            ]
            if roles is not None:
                logging.info(f"Someone consulted all roles at {datetime.now()}")
                res = make_response(roles, 200)
                res.headers['Access-Control-Allow-Origin'] = "*"
                return res
            else:
                return make_response({"message":"No roles found !"}, 202)
        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error retrieving get all roles : {e}"}, 500)
     
     
     
     
     
        
    def get_role(self, id):
        try:
            self.cur.execute("SELECT * FROM roles WHERE id=%s", (id,))
            row = self.cur.fetchone()
            if row is not None:
                role = dict(id=row[0], name=row[1], description=row[2])
                sql = '''SELECT name FROM roles WHERE id=%s'''
                self.cur.execute(sql, (id,))
                role_name = self.cur.fetchone()[0]
                logging.info(f"Someone consulted role with id : [ {id} ] and name : [ {role_name} ] at {datetime.now()}")
                res = make_response(role, 200)
                res.headers['Access-Control-Allow-Origin'] = "*"
                return res
            else:
                return make_response({"message":"No role found !"}, 202)
        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error retrieving get role : {e}"}, 500)
      
      
      
      
            
    def add_role(self, data):
        try:
            data_str = data.decode('utf-8')
            data_dict = json.loads(data_str)

            new_name = data_dict['name']
            new_description = data_dict['description']

            # Check if a role with the same name (ignoring case) already exists
            self.cur.execute("SELECT id FROM roles WHERE lower(name) = %s", (new_name.lower(),))
            existing_role = self.cur.fetchone()
            if existing_role:
                return make_response({"message": f"Role with name {new_name} already exists"}, 400)

            # Add the new role
            sql = """INSERT INTO roles (name, description)
                    VALUES (%s, %s)"""
            self.cur.execute(sql, (new_name, new_description))
            self.conn.commit()
            self.cur.execute("SELECT currval(pg_get_serial_sequence('roles', 'id'));")
            role_id = self.cur.fetchone()[0] 
            logging.info(f"The role with id : [ {role_id} ] and name : [ {new_name} ] has been added at {datetime.now()}")
            res = make_response({"message": f"Role with id: {role_id} and name: {new_name} created successfully"}, 201)
            res.headers['Access-Control-Allow-Origin'] = "*"
            return res
        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error adding role : {e}"}, 500)

    def search_by_role_name(self, data):
        try:
            data_str = data.decode('utf-8')
            data_dict = json.loads(data_str)

            role_name = data_dict['role_name']
            if not role_name:
                return make_response({'error': 'missing name parameter'}, 400)

            # Recherche des rôles par nom avec les descriptions des permissions
            sql = """
                SELECT roles.id, roles.name as role_name, roles.description as role_description,
                (SELECT array_agg(permissions.description) FROM roles_permissions
                JOIN permissions ON roles_permissions.permission_id = permissions.id
                WHERE roles_permissions.role_id = roles.id) as permissions
                FROM roles
                WHERE roles.name LIKE %s
            """
            self.cur.execute(sql, ('%' + role_name + '%',))
            roles_data = self.cur.fetchall()

            roles = []
            for role_data in roles_data:
                role_dict = dict(id=role_data[0], name=role_data[1], description=role_data[2], permissions=role_data[3])
                roles.append(role_dict)

            # Retourne les rôles trouvés avec les descriptions des permissions
            return make_response({'roles': roles}, 200)

        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error retrieving update role : {e}"}, 500)



    def update_role(self, id, data):
        try:
            data_str = data.decode('utf-8')
            data_dict = json.loads(data_str)

            current_name = data_dict['name']
            current_description = data_dict['description']

            sql = """UPDATE roles
                    SET name=%s,
                        description=%s
                    WHERE id=%s"""
            self.cur.execute(sql, (current_name, current_description, id))
            self.conn.commit()

            # Return the updated role
            updated_role = {
                "name": current_name,
                "description": current_description
            }
            logging.info(f"The user with id : [ {id} ] and name : [ {current_name} ] has been modified at {datetime.now()}")
            res = make_response(updated_role, 201)
            res.headers['Access-Control-Allow-Origin'] = "*"
            return res
        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error retrieving update role : {e}"}, 500)
            
            
            
            
    def delete_role(self, id):
        try:
            self.cur.execute(f"DELETE from roles WHERE id=%s",(id,) )
            self.conn.commit()
            if self.cur.rowcount>0:
                logging.info(f"The role with id : [ {id} ] has been deleted at {datetime.now()}")
                res = make_response("Role deleted Successfully", 200)
                res.headers['Access-Control-Allow-Origin'] = "*"
                return res 
            else:
                return make_response("Nothing Deleted", 202)
        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error retrieving delete role : {e}"}, 500)
        
        
        
        
    # def patch_role(self, data, id):
    #     try:
    #         query = "UPDATE roles SET "
    #         for key in data:
    #             query += f"{key}='{data[key]}',"
    #         query = query[:-1] + f" WHERE id=%s"
    #         print(query)    
    #         self.cur.execute(query, (id,) )
    #         self.conn.commit()
    #         if self.cur.rowcount>0:
    #             return make_response({"message":"Role Updated in patch model successfully !"}, 201)
    #         else:
    #             return make_response({"message":"Nothing to Updated in patch model"}, 202)
    #     except Exception as e:
    #         self.conn.rollback()
    #         return make_response({"message": f"Error retrieving patch role : {e}"}, 500)