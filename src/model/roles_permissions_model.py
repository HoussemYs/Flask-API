from app import app
from flask import request, make_response, json
import psycopg2
from db.database import connect
from datetime import datetime
import logging


class roles_permissions():

    def __init__(self):
        try:
            self.conn, self.cur = connect()
        except psycopg2.Error as error:
            print(error)

    # def get_all_roles_permissions(self):
    #     try:
    #         self.cur.execute(
    #             "SELECT role_id, array_agg(permission_id) FROM roles_permissions GROUP BY role_id")
    #         self.conn.commit()
    #         roles_permissions = [
    #             dict(role_id=row[0], permission_ids=row[1])
    #             for row in self.cur.fetchall()
    #         ]
    #         if roles_permissions is not None:
    #             logging.info(f"Someone consulted all roles_permissions at {datetime.now()}")
    #             res = make_response(roles_permissions, 200)
    #             res.headers['Access-Control-Allow-Origin'] = "*"
    #             return res
    #         else:
    #             return make_response({"message": "No roles_permissions found !"}, 202)
    #     except Exception as e:
    #         self.conn.rollback()
    #         return make_response({"message": f"Error retrieving get all roles_permissions : {e}"}, 500)


    def get_all_roles_permissions(self):
        try:
            self.cur.execute(
                "SELECT r.name as role_name, array_agg(p.method || '  ' || p.endpoint) as permission_names, r.id as role_id, (SELECT array_agg(p2.id) FROM roles_permissions rp2 JOIN permissions p2 ON rp2.permission_id = p2.id WHERE rp2.role_id = r.id) as permission_ids FROM roles_permissions rp JOIN roles r ON rp.role_id = r.id JOIN permissions p ON rp.permission_id = p.id GROUP BY r.name, r.id"
            )
            self.conn.commit()
            roles_permissions = [
                dict(role_name=row[0], permission_names=row[1], role_id=row[2], permission_ids=row[3])
                for row in self.cur.fetchall()
            ]
            if roles_permissions is not None:
                logging.info(f"Someone consulted all roles_permissions at {datetime.now()}")
                res = make_response(roles_permissions, 200)
                res.headers['Access-Control-Allow-Origin'] = "*"
                return res
            else:
                return make_response({"message": "No roles_permissions found !"}, 202)
        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error retrieving get all roles_permissions : {e}"}, 500)


    def add_new_roles_permissions(self, data):
        try:
            data_str = data.decode('utf-8')
            data_dict = json.loads(data_str)

            role_id = data_dict['role_id']
            permission_id = data_dict['permission_id']

            # Check if the role and permission exist
            self.cur.execute("SELECT * FROM roles WHERE id=%s", (role_id,))
            role = self.cur.fetchone()
            if not role:
                return make_response({"message": "Role does not exist"}, 404)

            self.cur.execute(
                "SELECT * FROM permissions WHERE id=%s", (permission_id,))
            permission = self.cur.fetchone()
            if not permission:
                return make_response({"message": "Permission does not exist"}, 404)

            # Check if the role-permission relationship already exists
            self.cur.execute(
                "SELECT * FROM roles_permissions WHERE role_id=%s AND permission_id=%s", (role_id, permission_id))
            existing_relationship = self.cur.fetchone()
            if existing_relationship:
                return make_response({"message": "Role-permission relationship already exists"}, 409)

            sql = """INSERT INTO roles_permissions (role_id, permission_id)
                    VALUES (%s, %s)"""
            self.cur.execute(sql, (role_id, permission_id))
            self.conn.commit()
            if self.cur.rowcount > 0:
                logging.info(f"The permission with id : [ {permission_id} ] has been added to the role with id : [ {role_id} ] at {datetime.now()}")
                res = make_response({"message": "New role-permission relationship created successfully"}, 201)
                res.headers['Access-Control-Allow-Origin'] = "*"
                return res
        except Exception as e:
            self.conn.rollback()
            return make_response(f"Error adding new role-permission relationship: {e}", 500)


    def get_roles_permissions(self, role_id):
        try:
            self.cur.execute(
                "SELECT permission_id FROM roles_permissions WHERE role_id=%s", (role_id,))
            permission_rows = self.cur.fetchall()
            if permission_rows:
                permission_ids = [row[0] for row in permission_rows]
                permission_descriptions = []
                for permission_id in permission_ids:
                    self.cur.execute(
                        "SELECT description FROM permissions WHERE id=%s", (permission_id,))
                    permission_description = self.cur.fetchone()[0]
                    permission_descriptions.append(permission_description)
                self.cur.execute(
                    "SELECT name FROM roles WHERE id=%s", (role_id,))
                role_name = self.cur.fetchone()[0]
                result = {"role_id": role_id, "role_name": role_name,
                          "permission_ids": permission_ids, "permission_descriptions": permission_descriptions}
                logging.info(f"Someone consulted all permissions of the role with id : [ {role_id} ] at {datetime.now()}")
                res = make_response(result, 200)
                res.headers['Access-Control-Allow-Origin'] = "*"
                return res
            else:
                return make_response({"message": f"No permissions found for this role with id {role_id}!"}, 202)
        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error retrieving get role_permissions: {e}"}, 500)
    def delete_roles_permissions(self, role_id):
        try:
            # Get the user IDs associated with the specified role
            self.cur.execute("SELECT user_id FROM users_roles WHERE role_id=%s", (role_id,))
            user_ids = self.cur.fetchall()

            # Delete the role-permission relationships for the specified role
            self.cur.execute("DELETE FROM roles_permissions WHERE role_id=%s", (role_id,))

            # Delete the permissions associated with the role
            self.cur.execute("DELETE FROM permissions WHERE id IN (SELECT permission_id FROM roles_permissions WHERE role_id=%s)", (role_id,))

            # Delete the role from the users
            self.cur.execute("DELETE FROM users_roles WHERE role_id=%s", (role_id,))

            self.conn.commit()

            if self.cur.rowcount > 0:
                logging.info(f"All role-permission relationships and the associated permissions for role with id [{role_id}] have been DELETED at {datetime.now()}")

            res = make_response({"message": "Role-Permission relationships and associated permissions have been deleted successfully"}, 200)
            res.headers['Access-Control-Allow-Origin'] = "*"
            return res
        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error deleting Role-Permission relationships and associated permissions: {e}"}, 500)

    def add_new_role_allpermissions(self, data):
        try:
            data_dict = json.loads(data)

            role_id = data_dict['role_id']
            permission_ids = data_dict['permission_ids']

            # Check if the role exists
            self.cur.execute("SELECT * FROM roles WHERE id=%s", (role_id,))
            role = self.cur.fetchone()
            if not role:
                return make_response({"message": "Role does not exist"}, 404)

            # Check if all the permissions exist
            for permission_id in permission_ids:
                self.cur.execute("SELECT * FROM permissions WHERE id=%s", (permission_id,))
                permission = self.cur.fetchone()
                if not permission:
                    return make_response({"message": f"Permission with ID {permission_id} does not exist"}, 404)

                # Check if the role-permission relationship already exists
                self.cur.execute(
                    "SELECT * FROM roles_permissions WHERE role_id=%s AND permission_id=%s", (role_id, permission_id))
                existing_relationship = self.cur.fetchone()
                if existing_relationship:
                    return make_response({"message": f"Role-Permission relationship for permission ID {permission_id} already exists"}, 409)

            # Insert new role-permission relationships
            for permission_id in permission_ids:
                sql = """INSERT INTO roles_permissions (role_id, permission_id)
                        VALUES (%s, %s)"""
                self.cur.execute(sql, (role_id, permission_id))
                self.conn.commit()

            logging.info(f"Added new permissions with IDs {permission_ids} to role with ID {role_id} at {datetime.now()}")
            res = make_response({"message": "New role-permission relationships created successfully"}, 201)
            res.headers['Access-Control-Allow-Origin'] = "*"
            return res

        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error adding new role-permission relationships: {e}"}, 500)
  

    def update_role_permissions(self, role_id, data):
        try:
            data_dict = json.loads(data)
            permission_ids = data_dict['permission_ids']

            # Check if the role exists
            self.cur.execute("SELECT * FROM roles WHERE id=%s", (role_id,))
            role = self.cur.fetchone()
            if not role:
                return make_response({"message": "Role does not exist"}, 404)

            # Check if all the permissions exist
            for permission_id in permission_ids:
                self.cur.execute("SELECT * FROM permissions WHERE id=%s", (permission_id,))
                permission = self.cur.fetchone()
                if not permission:
                    return make_response({"message": f"Permission with ID {permission_id} does not exist"}, 404)

            # Delete existing role-permission relationships for the role
            self.cur.execute("DELETE FROM roles_permissions WHERE role_id=%s", (role_id,))

            # Insert new role-permission relationships
            for permission_id in permission_ids:
                sql = """INSERT INTO roles_permissions (role_id, permission_id)
                        VALUES (%s, %s)"""
                self.cur.execute(sql, (role_id, permission_id))
                self.conn.commit()

            logging.info(f"Updated permissions for role with ID {role_id} at {datetime.now()}")
            res = make_response({"message": "Role permissions updated successfully"}, 200)
            res.headers['Access-Control-Allow-Origin'] = "*"
            return res

        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error updating role permissions: {e}"}, 500)
        