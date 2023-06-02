from app import app
from flask import request, make_response, json
import psycopg2
from db.database import connect
from datetime import datetime
import logging



class users_roles():

    def __init__(self):
        try:
            self.conn, self.cur = connect()
        except psycopg2.Error as error:
            print(error)



    def get_all_users_roles(self):
        try:
            self.cur.execute("SELECT user_id, array_agg(role_id) FROM users_roles GROUP BY user_id")
            self.conn.commit()
            user_roles = []
            for row in self.cur.fetchall():
                user_id, role_ids = row
                self.cur.execute("SELECT username FROM users WHERE id=%s", (user_id,))
                username = self.cur.fetchone()[0]
                self.cur.execute("SELECT name FROM roles WHERE id=ANY(%s)", (role_ids,))
                role_names = [r[0] for r in self.cur.fetchall()]
                user_roles.append({"username": username, "roles_names": role_names, "username_id": user_id, "roles_ids": role_ids })
            if user_roles:
                logging.info(f"Someone consulted all users_roles at {datetime.now()}")
                res = make_response(user_roles, 200)
                res.headers['Access-Control-Allow-Origin'] = "*"
                return res
            else:
                return make_response({"message":"No users_roles found !"}, 202)
        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error retrieving get all users_roles : {e}"}, 500)





    # Add multiple roles to one user at the same time
    def add_new_user_roles(self, data):
        try:
            # data_str = data.decode('utf-8')
            # data_dict = json.loads(data_str)

            # user_id = data_dict['user_id']
            # role_ids = data_dict['role_ids']
            data_str = data.decode('utf-8')
            # data_dict = json.loads(data_str)

            # print(f"data: {data}")
            # print(f"data_dict: {data_dict}")

            # user_id = data_dict['user_id']
            # role_ids = data_dict['role_ids']
            data_dict = json.loads(data)
            user_id = data_dict['user_id']
            role_ids = data_dict['role_ids']

            # Check if the user exists
            self.cur.execute("SELECT * FROM users WHERE id=%s", (user_id,))
            user = self.cur.fetchone()
            if not user:
                return make_response({"message": "User does not exist"}, 404)

            # Check if all the roles exist
            for role_id in role_ids:
                self.cur.execute("SELECT * FROM roles WHERE id=%s", (role_id,))
                role = self.cur.fetchone()
                if not role:
                    return make_response({"message": f"Role with ID {role_id} does not exist"}, 404)

                # Check if the role-user relationship already exists
                self.cur.execute("SELECT * FROM users_roles WHERE user_id=%s AND role_id=%s", (user_id, role_id))
                existing_relationship = self.cur.fetchone()
                if existing_relationship:
                    return make_response({"message": f"User-Role relationship for role ID {role_id} already exists"}, 409)

            # Insert new role-user relationships
            for role_id in role_ids:
                sql = """INSERT INTO users_roles (user_id, role_id)
                        VALUES (%s, %s)"""
                self.cur.execute(sql, (user_id, role_id))
                self.conn.commit()

            logging.info(f"Added new roles with IDs {role_ids} to user with ID {user_id} at {datetime.now()}")
            res = make_response({"message": "New user-role relationships created successfully"}, 201)
            res.headers['Access-Control-Allow-Origin'] = "*"
            return res

        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error adding new user-role relationships: {e}"}, 500)
            

    
    # Add one role to one user
    def add_new_user_role(self, data):
        try:
            data_str = data.decode('utf-8')
            data_dict = json.loads(data_str)

            user_id = data_dict['user_id']
            role_id = data_dict['role_id']

            # Check if the user and role exist
            self.cur.execute("SELECT * FROM users WHERE id=%s", (user_id,))
            user = self.cur.fetchone()
            if not user:
                return make_response({"message": "User does not exist"}, 404)

            self.cur.execute("SELECT * FROM roles WHERE id=%s", (role_id,))
            role = self.cur.fetchone()
            if not role:
                return make_response({"message": "Role does not exist"}, 404)

            # Check if the role-permission relationship already exists
            self.cur.execute("SELECT * FROM users_roles WHERE user_id=%s AND role_id=%s", (user_id, role_id))
            existing_relationship = self.cur.fetchone()
            if existing_relationship:
                return make_response({"message": "User-Role relationship already exists"}, 409)

            sql = """INSERT INTO users_roles (user_id, role_id)
                    VALUES (%s, %s)"""
            self.cur.execute(sql, (user_id, role_id))
            self.conn.commit()
            if self.cur.rowcount>0:
                logging.info(f"Someone has been added new role with id : [ {role_id} ] to the user with id : [ {user_id} ] at {datetime.now()}")
                res = make_response({"message": "New user_role relationship created successfully"}, 201)
                res.headers['Access-Control-Allow-Origin'] = "*"
                return res
        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error adding new user_role relationship: {e}"}, 500)
        


    def get_user_roles(self, data):
        try:
            data_str = data.decode('utf-8')
            data_dict = json.loads(data_str)

            user_id = data_dict['user_id']

            self.cur.execute("SELECT role_id FROM users_roles WHERE user_id=%s", (user_id,))
            role_rows = self.cur.fetchall()
            if role_rows:
                role_ids = [row[0] for row in role_rows]
                role_names = []
                for role_id in role_ids:
                    self.cur.execute("SELECT name FROM roles WHERE id=%s", (role_id,))
                    role_name = self.cur.fetchone()[0]
                    role_names.append(role_name)
                self.cur.execute("SELECT username FROM users WHERE id=%s", (user_id,))
                user_name = self.cur.fetchone()[0]
                result = {"user_id": user_id, "user_name": user_name, "role_ids": role_ids, "role_names": role_names}
                logging.info(f"Someone has been consulted all roles of the user with id : [ {user_id} ] at {datetime.now()}")
                res = make_response(result, 200)
                res.headers['Access-Control-Allow-Origin'] = "*"
                return res
            else:
                return make_response({"message": f"No role found for this user with id {user_id}!"}, 202)
        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error retrieving get user_roles: {e}"}, 500)



    def delete_user_roles(self, user_id):
        try:
            # Delete the user-role relationships for the specified user
            self.cur.execute("DELETE FROM users_roles WHERE user_id=%s AND role_id <> 82", (user_id,))

            self.conn.commit()

            if self.cur.rowcount > 0:
                logging.info(f"All user-role relationships for user with id [{user_id}] have been DELETED at {datetime.now()}")

            res = make_response({"message": "User-Role relationships have been deleted successfully"}, 200)
            res.headers['Access-Control-Allow-Origin'] = "*"
            return res
        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error deleting User-Role relationships: {e}"}, 500)


    def update_role_user_relationship(self, user_id, data):
        try:
            data_dict = json.loads(data)
            role_ids = data_dict['role_ids']

            # Check if the user exists
            self.cur.execute("SELECT * FROM users WHERE id=%s", (user_id,))
            user = self.cur.fetchone()
            if not user:
                return make_response({"message": "User does not exist"}, 404)

            # Check if all the roles exist
            for role_id in role_ids:
                self.cur.execute("SELECT * FROM roles WHERE id=%s", (role_id,))
                role = self.cur.fetchone()
                if not role:
                    return make_response({"message": f"Role with ID {role_id} does not exist"}, 404)

            # Delete existing user-role relationships for the user
            self.cur.execute("DELETE FROM users_roles WHERE user_id=%s", (user_id,))

            # Insert new user-role relationships
            for role_id in role_ids:
                sql = """INSERT INTO users_roles (user_id, role_id)
                        VALUES (%s, %s)"""
                self.cur.execute(sql, (user_id, role_id))
                self.conn.commit()

            logging.info(f"Updated roles for user with ID {user_id} at {datetime.now()}")
            res = make_response({"message": "User roles updated successfully"}, 200)
            res.headers['Access-Control-Allow-Origin'] = "*"
            return res

        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error updating user roles: {e}"}, 500)
