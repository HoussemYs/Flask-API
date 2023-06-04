

# ************************CODE DESCRIPTION USERS_MODEL************************

    # all Functions get requests from controller
        # Function user_login : get the username and password from request body from client-side 
                    #and save the token in cookies with name token and value (token.value)
    
    # For the rest of function : check the token and if he have permission he can access to function
        # Function add_user : get the username and password passed from client-side
                        # and check if the username is not used from another user, then save the new user
        # Function update_user : get the username and password passed from client-side
                        # and make the updates of the user who have the id passed in path
        # Function delete_user : get the id in path for the user that will be deleted
                        # and make the delete of the user who have the id passed in path
        # Function get_user : get the id in path for the user searched
                        # and get the user who have the id=id_passed 
        # Function get_all_users : get all users with the informations : "id":1 , "username":"houssem", "password":"houssem", "type_id":1, role_id[1,2]





from app import app
from flask import request, make_response, jsonify, session
import psycopg2
from datetime import datetime, timedelta
import jwt
from db.database import connect
import json
import logging


class users():

    def __init__(self):
        try:
            self.conn, self.cur = connect()
        except psycopg2.Error as error:
                print(error)


    def user_login(self, data):
        try:
            data_str = data.decode('utf-8')
            data_dict = json.loads(data_str)
        
            username = data_dict['username']
            password = data_dict['password']

            self.cur.execute(
                "SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
            result = self.cur.fetchone()
            if not result:
                return make_response({"message": "Incorrect username or password"} , 401)
            
            # Check if user is banned
            if result[4]:
                return make_response({"message": "User is banned and cannot log in"} , 401)

            user_id = result[0]
            self.cur.execute(
                f"SELECT users_roles.role_id FROM users LEFT JOIN users_roles ON users.id = users_roles.user_id WHERE users.id = {user_id}")
            res = self.cur.fetchall()
            roles = [r[0] for r in res]
            payload = {
                "user_id": result[0],
                "username": result[1],
                "password": result[2],
                "type_id": result[3],
                "role_id": roles,
                "exp": int((datetime.now() + timedelta(minutes=45)).timestamp())
            }
            jwtoken = jwt.encode(payload, "HoussemYousfi", algorithm="HS256")
            response_data = {
                'token': jwtoken,
                'user_id': result[0],
                'username': result[1],
                'password': result[2],
                'type_id': result[3],
                'role_id': roles,
            }
            # response = make_response({'token': jwtoken}, 200)
            response = make_response(response_data, 200)
            response.headers['Authorization'] = f'Bearer {jwtoken}'
            response.headers['Access-Control-Allow-Origin'] = "*"
            logging.info(f"{username} has logged in at {datetime.now()}")
            return response

        except Exception as e:
            return make_response({"erreur": str(e)}, 500)

    # def user_login(self, data):
    #     try:
    #         data_str = data.decode('utf-8')
    #         data_dict = json.loads(data_str)

    #         username = data_dict['username']
    #         password = data_dict['password']

    #         self.cur.execute(
    #             "SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
    #         result = self.cur.fetchone()
    #         if not result:
    #             return make_response({"message": "Incorrect username or password"}, 401)

    #         # Check if user is banned
    #         if result[4]:
    #             return make_response({"message": "User is banned and cannot log in"}, 401)

    #         user_info = {
    #             "user_id": result[0],
    #             "username": result[1],
    #             "password": result[2],
    #             "type_id": result[3]
    #         }

    #         session['user_info'] = user_info

    #         self.cur.execute(
    #             f"SELECT role_id FROM users_roles WHERE user_id = {result[0]}"
    #         )
    #         roles = [r[0] for r in self.cur.fetchall()]

    #         payload = {
    #             "user_id": result[0],
    #             "username": result[1],
    #             "password": result[2],
    #             "type_id": result[3],
    #             "role_id": roles,
    #             "exp": int((datetime.now() + timedelta(minutes=45)).timestamp())
    #         }
    #         jwtoken = jwt.encode(payload, "HoussemYousfi", algorithm="HS256")
    #         response_data = {
    #             'token': jwtoken,
    #             'user_id': result[0],
    #             'username': result[1],
    #             'type_id': result[3],
    #             'role_id': roles,
    #         }

    #         response = make_response(response_data, 200)
    #         response.headers['Authorization'] = f'Bearer {jwtoken}'
    #         response.headers['Access-Control-Allow-Origin'] = "*"
    #         logging.info(f"{username} has logged in at {datetime.now()}")
    #         return response

    #     except Exception as e:
    #         return make_response({"erreur": str(e)}, 500)



    def search_user_by_username(self, data):
        try:
            data_str = data.decode('utf-8')
            data_dict = json.loads(data_str)

            username = data_dict['username']
            if not username:
                return make_response({'error': 'missing name parameter'}, 400)

            # recherche des users par nom
            self.cur.execute("""SELECT users.id, users.username, roles.name
                                FROM users
                                JOIN users_roles ON users.id = users_roles.user_id
                                JOIN roles ON roles.id = users_roles.role_id
                                WHERE users.username LIKE %s""",
                            ('%' + username + '%',))
            users_data = self.cur.fetchall()

            users = {}
            for user_data in users_data:
                user_id = user_data[0]
                username = user_data[1]
                role = user_data[2]
                if user_id not in users:
                    users[user_id] = {'id': user_id, 'username': username, 'roles': []}
                users[user_id]['roles'].append(role)

            users_list = list(users.values())

            return make_response({'users': users_list}, 200)

        except Exception as e:
            print(e)
            return make_response({'error': 'internal server error'}, 500)



    def get_all_users(self):
        try:
            self.cur.execute("SELECT * FROM users")
            users = []
            for row in self.cur.fetchall():
                self.cur.execute(
                    "SELECT name FROM types WHERE id=%s", (row[3],))
                type_res = self.cur.fetchone()
                self.cur.execute(
                    "SELECT role_id FROM users_roles WHERE user_id=%s", (row[0],))
                
                role_res = self.cur.fetchall()
                role_ids = [r[0] for r in role_res]
                roles = []
                for role_id in role_res:
                    self.cur.execute(
                        "SELECT name FROM roles WHERE id=%s", (role_id,))
                    role_name_res = self.cur.fetchone()
                    if role_name_res:
                        role_name = role_name_res[0]
                        roles.append(role_name)
                user = dict(id=row[0], username=row[1], password=row[2],
                            type_id=row[3], USER_TYPE=type_res[0], role_id=role_ids , roles=roles)
                users.append(user)
            if users:
                logging.info(f"Someone consulted all users at {datetime.now()}")
                res = make_response(users, 200)
                res.headers['Access-Control-Allow-Origin'] = "*"
                return res
            else:
                return make_response({"message": "No users found !"}, 202)
        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error retrieving all users: {e}"}, 500)
        

    # def add_user(self, data):
    #     try:
    #         data_str = data.decode('utf-8')
    #         data_dict = json.loads(data_str)

    #         new_username = data_dict['username']
    #         new_password = data_dict['password']
    #         new_role = data_dict['role']
    #         new_type_id = 1
    #         new_role_lower = new_role.lower()

    #         # Check if the username already exists (ignoring case)
    #         self.cur.execute("SELECT id FROM users WHERE lower(username) = %s", (new_username.lower(),))
    #         existing_user = self.cur.fetchone()
    #         if existing_user:
    #             return make_response({"message": f"Username {new_username} already exists"}, 400)

    #         # Check if the role exists (ignoring case)
    #         self.cur.execute("SELECT id FROM roles WHERE lower(name) = %s", (new_role_lower,))
    #         existing_role = self.cur.fetchone()
    #         if not existing_role:
    #             return make_response({"message": f"Role '{new_role}' not found"}, 400)

    #         # Add the new user
    #         sql = """INSERT INTO users (username, password, type_id)
    #                 VALUES (%s, %s, %s)"""
    #         self.cur.execute(sql, (new_username, new_password, new_type_id))
    #         self.conn.commit()

    #         self.cur.execute("SELECT currval(pg_get_serial_sequence('users', 'id'));")
    #         user_id = self.cur.fetchone()[0]

    #         sql = """INSERT INTO users_roles (user_id, role_id)
    #                 VALUES (%s, %s)"""
    #         self.cur.execute(sql, (user_id, existing_role[0]))
    #         self.conn.commit()

    #         logging.info(f"The user with id : [ {user_id} ] and name : [ {new_username} ] has been added in at {datetime.now()}")
    #         res = make_response({"message": f"User with the id: {user_id} and name: {new_username} created successfully"}, 201)
    #         res.headers['Access-Control-Allow-Origin'] = "*"
    #         return res
    #     except Exception as e:
    #         self.conn.rollback()
    #         return make_response({"message": f"Error adding user: {e}"}, 500)

    def add_user(self, data):
        try:
            data_str = data.decode('utf-8')
            data_dict = json.loads(data_str)

            new_username = data_dict['username']
            new_password = data_dict['password']
            new_role = data_dict['role']
            new_type_id = 1
            new_role_lower = new_role.lower()

            # Check if the username already exists (ignoring case)
            self.cur.execute("SELECT id FROM users WHERE lower(username) = %s", (new_username.lower(),))
            existing_user = self.cur.fetchone()
            if existing_user:
                return make_response({"message": f"Username {new_username} already exists"}, 400)

            # Check if the role exists (ignoring case)
            self.cur.execute("SELECT id FROM roles WHERE lower(name) = %s", (new_role_lower,))
            existing_role = self.cur.fetchone()
            if not existing_role:
                return make_response({"message": f"Role '{new_role}' not found"}, 400)

            # Add the new user
            sql = """INSERT INTO users (username, password, type_id)
                    VALUES (%s, %s, %s)"""
            self.cur.execute(sql, (new_username, new_password, new_type_id))
            self.conn.commit()

            self.cur.execute("SELECT currval(pg_get_serial_sequence('users', 'id'));")
            user_id = self.cur.fetchone()[0]

            # Add the default role for the new user
            self.cur.execute("SELECT id FROM roles WHERE name = 'default role'")
            default_role = self.cur.fetchone()
            if not default_role:
                return make_response({"message": "Default role not found"}, 400)

            sql = """INSERT INTO users_roles (user_id, role_id)
                    VALUES (%s, %s)"""
            self.cur.execute(sql, (user_id, default_role[0]))
            self.conn.commit()

            # Add any additional roles specified during user creation
            if new_role != 'default role':
                self.cur.execute("SELECT id FROM roles WHERE name = %s", (new_role,))
                additional_role = self.cur.fetchone()
                if not additional_role:
                    return make_response({"message": f"Role '{new_role}' not found"}, 400)

                sql = """INSERT INTO users_roles (user_id, role_id)
                        VALUES (%s, %s)"""
                self.cur.execute(sql, (user_id, additional_role[0]))
                self.conn.commit()

            logging.info(f"The user with id: [{user_id}] and name: [{new_username}] has been added at {datetime.now()}")
            res = make_response({"message": f"User with the id: {user_id} and name: {new_username} created successfully"}, 201)
            res.headers['Access-Control-Allow-Origin'] = "*"
            return res
        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error adding user: {e}"}, 500)

    def get_user(self, id):
        try:
            self.cur.execute("SELECT * FROM users WHERE id=%s", (id,))
            row = self.cur.fetchone()
            if row is not None:
                self.cur.execute(
                    "SELECT name FROM types WHERE id=%s", (row[3],))
                type_res = self.cur.fetchone()
                if type_res is not None:
                    user = dict(id=row[0], username=row[1], password=row[2],
                                type_id=row[3], USER_TYPE=type_res[0])
                sql = '''SELECT username FROM users WHERE id=%s'''
                self.cur.execute(sql, (id,))
                user_name = self.cur.fetchone()[0]
                logging.info(f"Someone consulted user with id : [ {id} ] and name : [ {user_name} ] at {datetime.now()}")
                res = make_response(user, 200)
                res.headers['Access-Control-Allow-Origin'] = "*"
                return res
            else:
                return make_response({"message": "No user found !"}, 202)
        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error retrieving get user : {e}"}, 500)


    def update_user(self, id, data):
        try:
            data_str = data.decode('utf-8')
            data_dict = json.loads(data_str)

            current_username = data_dict['username']
            current_password = data_dict['password']
            new_role = data_dict['role']  # New role to assign

            # Check if the role exists
            new_role_lower = new_role.lower()
            self.cur.execute("SELECT id FROM roles WHERE lower(name) = %s", (new_role_lower,))
            new_role_id = self.cur.fetchone()
            if not new_role_id:
                return make_response({"message": f"Role '{new_role}' does not exist"}, 404)

            sql = """UPDATE users
                    SET username=%s,
                        password=%s
                    WHERE id=%s"""
            self.cur.execute(sql, (current_username, current_password, id))
            self.conn.commit()

            # Update the role of the user
            self.cur.execute("UPDATE users_roles SET role_id = %s WHERE user_id = %s", (new_role_id[0], id))
            self.conn.commit()

            # Return the updated user
            updated_user = {
                "username": current_username,
                "password": current_password,
                "role": new_role
            }
            logging.info(f"The user with id: [{id}] and name: [{current_username}] has been modified at {datetime.now()}")
            res = make_response(updated_user, 201)
            res.headers['Access-Control-Allow-Origin'] = "*"
            return res
        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error updating user: {e}"}, 500)

    def delete_user(self, id):
        try:
            self.cur.execute(f"DELETE FROM users WHERE id = %s", (id,))
            self.conn.commit()
            if self.cur.rowcount > 0:
                logging.info(f"The user with id : [ {id} ] has been deleted at {datetime.now()}")
                res = make_response("User deleted Successfully", 200)
                res.headers['Access-Control-Allow-Origin'] = "*"
                return res 
            else:
                return make_response("Nothing Deleted", 202)
        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error retrieving delete user : {e}"}, 500)

    def ban_user(self, id):
        try:
            self.cur.execute("""
                UPDATE users 
                SET banned = CASE 
                    WHEN banned = True THEN False 
                    ELSE True 
                END 
                WHERE id=%s
            """, (id,))
            self.conn.commit()
            if self.cur.rowcount > 0:
                logging.info(f"The user with id : [ {id} ] has been banned/unbanned at {datetime.now()}")
                res = make_response(f"User with id {id} has been banned/unbanned successfully", 200)
                res.headers['Access-Control-Allow-Origin'] = "*"
                return res
            else:
                return make_response({"message": "No user found!"}, 202)
        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error toggling user ban: {e}"}, 500)


    def get_all_banned_users(self):
        try:
            self.cur.execute("SELECT * FROM users WHERE banned=True")
            rows = self.cur.fetchall()
            users = []
            for row in rows:
                self.cur.execute(
                    "SELECT name FROM types WHERE id=%s", (row[3],))
                type_res = self.cur.fetchone()
                if type_res is not None:
                    user = dict(id=row[0], username=row[1], password=row[2],
                                type_id=row[3], USER_TYPE=type_res[0], banned=row[4])
                    users.append(user)
            if len(users) > 0:
                logging.info(f"{len(users)} banned users retrieved at {datetime.now()}")
                res = make_response({"Enable/Disable Successfu ": users}, 200)
                res.headers['Access-Control-Allow-Origin'] = "*"
                return res
            else:
                return make_response({"message": "No users found!"}, 202)
        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error retrieving all users: {e}"}, 500)
