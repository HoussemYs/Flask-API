from app import app
from flask import request, make_response, json
import psycopg2
from db.database import connect
from datetime import datetime
import logging
import os


class configurations():
    
    

    def __init__(self):
        try:
            self.conn, self.cur = connect()
        except psycopg2.Error as error:
            print(error)
            

    def search_configurations(self, term):
        try:
            self.cur.execute("SELECT * FROM configurations WHERE name ILIKE %s ORDER BY id ASC", ('%' + term + '%',))
            configurations = [
                {
                    "id": row[0],
                    "name": row[1],
                    "value": row[2],
                    "defaultValue": row[3],
                    "createdAt": row[4],
                    "createdBy": row[5],
                    "updatedBy": row[6],
                    "description": row[7],
                    "version": row[8]
                }
                for row in self.cur.fetchall()
            ]
            
            if configurations:
                return make_response(configurations, 200)
            else:
                return make_response({"message": "No configurations found!"}, 202)
        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error retrieving configurations: {e}"}, 500)
        
    def search_versions(self, term):
        try:
            self.cur.execute("SELECT * FROM configuration_versions WHERE name ILIKE %s ORDER BY id ASC", ('%' + term + '%',))
            versions = [
                {
                    "id": row[0],
                    "name": row[1],
                    "value": row[2],
                    "updatedBy": row[3],
                    "description": row[4],
                    "version": row[5],
                    "id_configuration": row[6],
                    "versionningAt": row[7]
                }
                for row in self.cur.fetchall()
            ]
            
            if versions:
                return make_response(versions, 200)
            else:
                return make_response({"message": "No versions found!"}, 202)
        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error retrieving versions: {e}"}, 500)
        

    
    def get_all_configurations(self):
        try:
            self.cur.execute("SELECT * FROM configurations ORDER BY id ASC")
            self.conn.commit()
            configurations = []

            for row in self.cur.fetchall():
                configuration = {
                    "id": row[0],
                    "name": row[1],
                    "value": None,  # Placeholder for file content or value
                    "defaultValue": row[3],
                    "createdAt": row[4],
                    "createdBy": row[5],
                    "updatedBy": row[6],
                    "description": row[7],
                    "version": row[8]
                }

                file_path = row[2]
                if file_path:  # Check if value is a file path
                    if os.path.isfile(file_path):
                        with open(file_path, 'r') as file:
                            file_content = file.read()
                            try:
                                json_data = json.loads(file_content)
                                text_value = json_data.get("text", "")
                                configuration["value"] = text_value
                            except json.JSONDecodeError:
                                configuration["value"] = "Invalid file content (not in JSON format)"
                    else:
                        # configuration["value"] = "File not found"
                        configuration["value"] = file_path
                # else:  # Handle normal string value or empty value
                #     value = row[2]
                #     if value:
                #         configuration["value"] = value
                #     else:
                #         configuration["value"] = "Empty value"

                configurations.append(configuration)

            if configurations:
                res = make_response(configurations, 200)
                # res.headers['Access-Control-Allow-Origin'] = "*"
                return res
            else:
                return make_response({"message": "No configurations found!"}, 202)
        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error retrieving get all configurations: {e}"}, 500)

    
    # def get_all_configurations(self):
    #     try:
    #         self.cur.execute("SELECT * FROM configurations ORDER BY id ASC")
    #         self.conn.commit()
    #         configurations = [
    #             dict(id=row[0], name=row[1], value=row[2], defaultValue=row[3], 
    #                  createdAt=row[4], createdBy=row[5], updatedBy=row[6], 
    #                  description=row[7], version=row[8])
    #             for row in self.cur.fetchall()
    #         ]
    #         if configurations is not None:
    #             res = make_response(configurations, 200)
    #             # res.headers['Access-Control-Allow-Origin'] = "*"
    #             return res  
    #         else:
    #             return make_response({"message":"No configurations found !"}, 202)
    #     except Exception as e:
    #         self.conn.rollback()
    #         return make_response({"message": f"Error retrieving get all configurations : {e}"}, 500)
        
        
        
        
        
        
    def get_configuration(self, id):
        try:
            self.cur.execute("SELECT * FROM configurations WHERE id=%s", (id,))
            row = self.cur.fetchone()
            if row is not None:
                configuration = dict(id=row[0], name=row[1], value=None, defaultValue=row[3], 
                     createdAt=row[4], createdBy=row[5], updatedBy=row[6], 
                     description=row[7], version=row[8])
                
                file_path = row[2]
                if file_path:  # Check if value is a file path
                    if os.path.isfile(file_path):
                        with open(file_path, 'r') as file:
                            file_content = file.read()
                            try:
                                json_data = json.loads(file_content)
                                text_value = json_data.get("text", "")
                                configuration["value"] = text_value
                            except json.JSONDecodeError:
                                configuration["value"] = "Invalid file content (not in JSON format)"
                    else:
                        # configuration["value"] = "File not found"
                        configuration["value"] = file_path
                
                return make_response(configuration, 200)
            else:
                return make_response({"message":"No configuration found !"}, 202)
        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error retrieving get configuration : {e}"}, 500)

    def add_configuration(self, data):
        try:
            new_name = data['name']
            new_createdAt = datetime.now()
            new_description = data['description']
            new_version = 1
            new_user_id = data['user_id']
            new_value = data['value']

            # Vérifier si l'utilisateur existe
            self.cur.execute("SELECT id FROM users WHERE id = %s", (new_user_id,))
            user = self.cur.fetchone()
            if not user:
                return make_response("Utilisateur introuvable", 404)

            # Récupérer le nom de profil correspondant à l'utilisateur
            self.cur.execute("SELECT name FROM profiles WHERE user_id = %s", (new_user_id,))
            profile = self.cur.fetchone()
            if not profile:
                return make_response("Profil introuvable", 404)

            new_createdBy = profile[0]  # Récupérer le nom de l'utilisateur

            # Check if configuration with the same name exists (case-insensitive)
            self.cur.execute("SELECT id FROM configurations WHERE LOWER(name) = %s", (new_name.lower(),))
            existing_config = self.cur.fetchone()
            if existing_config:
                return make_response({"message": f"Configuration with name '{new_name}' already exists."}, 400)

            # Insert new configuration into the configurations table
            sql = """INSERT INTO configurations (name, value, defaultValue, createdAt, createdBy, description, version)
                    VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id"""
            self.cur.execute(sql, (new_name, new_value, new_value,
                                new_createdAt, new_createdBy, new_description, new_version))
            configuration_id = self.cur.fetchone()[0]
            if not configuration_id:
                # No ID was returned, so roll back the transaction and raise an exception
                self.conn.rollback()
                raise Exception("Failed to retrieve the last inserted configuration ID")
            self.conn.commit()

            # Insert the new configuration into the versions table
            sql = """INSERT INTO configuration_versions (name, value, versionningAt, updatedBy, description, version, id_configuration)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            self.cur.execute(sql, (new_name, new_value, new_createdAt, new_createdBy, new_description, new_version, configuration_id))
            if self.cur.rowcount == 0:
                # No rows were inserted, so roll back the transaction and raise an exception
                self.conn.rollback()
                raise Exception("Failed to insert row into versions table")
            self.conn.commit()

            return make_response({"message": f"Configuration with id {configuration_id} created successfully."}, 201)

        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error retrieving add configuration: {e}"}, 500)


    # def add_configuration(self, data):
    #     try:
    #         new_name = data['name']
    #         new_value = data['value']
    #         new_createdAt = datetime.now()
    #         new_description = data['description']
    #         new_version = 1
    #         new_user_id = data['user_id']
    #         # Vérifier si l'utilisateur existe
    #         self.cur.execute("SELECT id FROM users WHERE id = %s", (new_user_id,))
    #         user = self.cur.fetchone()
    #         if not user:
    #             return "Utilisateur introuvable", 404
    #         # Récupérer le nom de profil correspondant à l'utilisateur
    #         self.cur.execute("SELECT name FROM profiles WHERE user_id = %s", (new_user_id,))
    #         profile = self.cur.fetchone()
    #         if not profile:
    #             return "Profil introuvable", 404
    #         new_createdBy = profile[0]  # Récupérer le nom de l'utilisateur

    #         # Check if configuration with the same name exists (case-insensitive)
    #         self.cur.execute("SELECT id FROM configurations WHERE LOWER(name) = %s", (new_name.lower(),))
    #         existing_config = self.cur.fetchone()
    #         if existing_config:
    #             return make_response({"message": f"Configuration with name '{new_name}' already exists."}, 400)

    #         # Insert new configuration into the configurations table
    #         sql = """INSERT INTO configurations (name, value, defaultValue, createdAt, createdBy, description, version)
    #                 VALUES (%s, %s, %s, %s, %s, %s, %s)"""
    #         self.cur.execute(sql, (new_name, new_value, new_value,
    #                     new_createdAt, new_createdBy, new_description, new_version))
    #         if self.cur.rowcount == 0:
    #             # No rows were inserted, so roll back the transaction and raise an exception
    #             self.conn.rollback()
    #             raise Exception("Failed to insert row into configurations table")
    #         self.conn.commit()
    #         self.cur.execute("SELECT currval(pg_get_serial_sequence('configurations', 'id'));")
    #         configuration_id = self.cur.fetchone()[0]

    #         # Insert the new configuration into the configuration_versions table
    #         sql = """INSERT INTO configuration_versions (name, value, updatedBy, description, version, id_configuration)
    #                 VALUES (%s, %s, %s, %s, %s, %s)"""
    #         self.cur.execute(sql, (new_name, new_value, new_createdBy, new_description, new_version, configuration_id))
    #         if self.cur.rowcount == 0:
    #             # No rows were inserted, so roll back the transaction and raise an exception
    #             self.conn.rollback()
    #             raise Exception("Failed to insert row into configuration_versions table")
    #         self.conn.commit()

    #         return make_response({"message": f"Configuration with id {configuration_id} created successfully."}, 201)

    #     except Exception as e:
    #         self.conn.rollback()
    #         return make_response({"message": f"Error retrieving add profile: {e}"}, 500)


    def patch_configuration(self, id, data):
        try:
            query = "UPDATE configurations SET "
            for key in data:
                query += f"{key}='{data[key]}',"
            query = query[:-1] + f" WHERE id=%s"
            # print(query)    
            self.cur.execute(query, (id,) )
            self.conn.commit()
            if self.cur.rowcount>0:
                #FOR VERSIONNING
                self.cur.execute("SELECT version FROM configurations WHERE id=%s", (id,))
                version = self.cur.fetchone()
                if version is not None:
                    new_version = version[0] + 1
                    sql_query = "UPDATE configurations SET version=%s WHERE id=%s"
                    self.cur.execute(sql_query, (new_version, id, ))
                    return make_response({"message":f"version was {version} and be {new_version} and configuration patched in database successfully (model)"}, 201)
                # return make_response({"message":"configuration patched in database successfully (model) !"}, 201)
            else:
                return make_response({"message":"Nothing to Updated in patch model"}, 202)
                            
        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error retrieving patch user : {e}"}, 500)
    
        
 
    # def update_configuration(self, id, data, request):
    #     try:
    #         user_id = request.json['user_id']
            
    #         # Récupérer l'id du user correspondant
    #         self.cur.execute("SELECT id FROM users WHERE id = %s", (user_id,))
    #         user_id = self.cur.fetchone()
    #         if user_id is not None:
    #             user_id = user_id[0]
                
    #         # Récupérer l'id du profile correspondant
    #         self.cur.execute("SELECT name FROM profiles WHERE user_id = %s", (user_id,))
    #         profile_name = self.cur.fetchone()
    #         if not profile_name:
    #             return make_response({"message": "No profile found!"}, 404)
    #         profile_name = profile_name[0]
            
    #         sql = """INSERT INTO user_configurations (user_id, configuration_id)
    #             VALUES (%s, %s)
    #             ON CONFLICT (user_id, configuration_id)
    #             DO UPDATE SET user_id = %s, configuration_id = %s"""
    #         self.cur.execute(sql, (user_id, id, user_id, id))
    #         self.conn.commit()
            
    #         name = request.json["name"]
    #         value = request.json["value"]
    #         description = request.json["description"]
    #         new_version = request.json["version"]

          
    #         updated_configurations = {
    #             "name": name,
    #             "value": value,
    #             "updatedBy": profile_name,
    #             "description": description,
    #             "version": new_version
    #         }
            
    #         # Mettre à jour la configuration avec le nom du profil dans le champ updatedBy
    #         sql = """UPDATE configurations
    #                 SET name=%s,
    #                     value=%s,
    #                     updatedBy=%s,
    #                     description=%s,
    #                     version=%s
    #                 WHERE id=%s"""
    #         self.cur.execute(sql, (name, value, profile_name, description, new_version, id))
    #         self.conn.commit()
    #         return make_response(updated_configurations, 200)
    #         # self.cur.close()
    #     except Exception as e:
    #         self.conn.rollback()
    #         return make_response({"message": f"Error retrieving update configuration model : {e}"}, 500)


    def update_configuration(self, id, data, request):
        try:
            user_id = request.json['user_id']

            # Récupérer l'id du user correspondant
            self.cur.execute("SELECT id FROM users WHERE id = %s", (user_id,))
            user_id = self.cur.fetchone()
            if user_id is not None:
                user_id = user_id[0]

            # Récupérer l'id du profile correspondant
            self.cur.execute("SELECT name FROM profiles WHERE user_id = %s", (user_id,))
            profile_name = self.cur.fetchone()
            if not profile_name:
                return make_response({"message": "No profile found!"}, 404)
            profile_name = profile_name[0]

            sql = """INSERT INTO user_configurations (user_id, configuration_id)
                VALUES (%s, %s)
                ON CONFLICT (user_id, configuration_id)
                DO UPDATE SET user_id = %s, configuration_id = %s"""
            self.cur.execute(sql, (user_id, id, user_id, id))
            self.conn.commit()

            name = request.json["name"]
            value = request.json["value"]
            description = request.json["description"]
            new_version = request.json["version"]

            updated_configurations = {
                "name": name,
                "value": value,
                "updatedBy": profile_name,
                "description": description,
                "version": new_version
            }

            # Mettre à jour la configuration avec le nom du profil dans le champ updatedBy
            sql = """UPDATE configurations
                    SET name=%s,
                        value=%s,
                        updatedBy=%s,
                        description=%s,
                        version=%s
                    WHERE id=%s"""
            self.cur.execute(sql, (name, value, profile_name, description, new_version, id))
            self.conn.commit()

            # Update the description in the version_configuration table
            sql = """UPDATE configuration_versions
                    SET description = %s
                    WHERE id_configuration = %s AND version = %s"""
            self.cur.execute(sql, (description,id, new_version))
            self.conn.commit()

            return make_response(updated_configurations, 200)
            # self.cur.close()
        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error retrieving update configuration model : {e}"}, 500)

    def delete_configuration(self, id):
        try:
            # Delete from configuration_versions table
            self.cur.execute("DELETE FROM configuration_versions WHERE id_configuration = %s", (id,))
            self.conn.commit()
            if self.cur.rowcount > 0:
                print("Deleted from configuration_versions successfully!")

            # Delete from user_configurations table
            self.cur.execute("DELETE FROM user_configurations WHERE configuration_id = %s", (id,))
            self.conn.commit()
            if self.cur.rowcount > 0:
                print("Deleted from user_configurations successfully!")

            # Delete from configurations table
            self.cur.execute("DELETE FROM configurations WHERE id = %s", (id,))
            self.conn.commit()
            if self.cur.rowcount > 0:
                print("Deleted from configurations successfully!")

            return make_response("Configuration deleted successfully", 200)

        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error deleting configuration: {e}"}, 500)







        #                       TABLE CONFIGURATION VERSION








    # def versionner_configuration(self, id, data, request):
    #     try:
    #         user_id = request.json['user_id']

    #         # Récupérer l'id du user correspondant
    #         self.cur.execute("SELECT id FROM users WHERE id = %s", (user_id,))
    #         user_id = self.cur.fetchone()
    #         if user_id is not None:
    #             user_id = user_id[0]

    #         # Récupérer l'id du profile correspondant
    #         self.cur.execute("SELECT name FROM profiles WHERE user_id = %s", (user_id,))
    #         profile_name = self.cur.fetchone()
    #         if not profile_name:
    #             return make_response({"message": "No profile found!"}, 404)
    #         profile_name = profile_name[0]

    #         # Récupérer la version actuelle de la configuration
    #         self.cur.execute("SELECT version FROM configurations WHERE id=%s", (id,))
    #         version = self.cur.fetchone()
    #         if version is not None:
    #             new_version = version[0] + 1
    #         else:
    #             new_version = 1

    #         # Mettre à jour la configuration actuelle avec la nouvelle version
    #         sql = """UPDATE configurations
    #                 SET value=%s,
    #                     updatedBy=%s,
    #                     description=%s,
    #                     version=%s
    #                 WHERE id=%s"""
    #         self.cur.execute(sql, (request.json["value"], profile_name, request.json["description"], new_version, id))
    #         self.conn.commit()

    #         # Insérer la nouvelle version de la configuration dans la table configuration_versions
    #         sql = """INSERT INTO configuration_versions (name, value, updatedBy, description, version, id_configuration)
    #                 SELECT name, value, updatedBy, description, version, id
    #                 FROM configurations
    #                 WHERE id = %s
    #                 RETURNING id"""
    #         self.cur.execute(sql, (id,))
    #         inserted_id = self.cur.fetchone()[0]
    #         self.conn.commit()

    #         updated_configurations = {
    #             "name": request.json["name"],
    #             "value": request.json["value"],
    #             "updatedBy": profile_name,
    #             "description": request.json["description"],
    #             "version": new_version
    #         }

    #         # Afficher les configurations actuelles
    #         self.cur.execute("SELECT * FROM configuration_versions")
    #         configurations = self.cur.fetchall()
    #         print(len(configurations))
    #         for configuration in configurations:
    #             print(configuration)


    #         return make_response(updated_configurations, 200)

    #     except Exception as e:
    #         self.conn.rollback()
    #         return make_response({"message": f"Error retrieving update configuration model: {e}"}, 500)


    def versionner_configuration(self, id, data, request):
        try:
            user_id = request.json['user_id']
            new_versionningAt = datetime.now()

            # Récupérer l'id du user correspondant
            self.cur.execute("SELECT id FROM users WHERE id = %s", (user_id,))
            user_id = self.cur.fetchone()
            if user_id is not None:
                user_id = user_id[0]

            # Récupérer l'id du profile correspondant
            self.cur.execute("SELECT name FROM profiles WHERE user_id = %s", (user_id,))
            profile_name = self.cur.fetchone()
            if not profile_name:
                return make_response({"message": "No profile found!"}, 404)
            profile_name = profile_name[0]

            # # Récupérer la dernière version de la configuration depuis la table configuration_versions
            # self.cur.execute("""
            #     SELECT version, value
            #     FROM configuration_versions
            #     WHERE id_configuration = %s
            #     ORDER BY version DESC
            #     LIMIT 1
            # """, (id,))
            # configuration_data = self.cur.fetchone()
            # if configuration_data is not None:
            #     version, current_value = configuration_data
            #     if current_value == request.json["value"]:
            #         return make_response({"message": "Version of configuration already exists"}, 400)
            #     new_version = version + 1
            # else:
            #     return make_response({"message": "Configuration not found!"}, 404)

            # Récupérer la dernière version de la configuration depuis la table configuration_versions
            self.cur.execute("""
                SELECT version, value
                FROM configuration_versions
                WHERE id_configuration = %s
                ORDER BY version DESC
                LIMIT 1
            """, (id,))
            configuration_data = self.cur.fetchone()
            if configuration_data is not None:
                version, current_file_path = configuration_data
                # Read the content of the current file
                with open(current_file_path, 'r') as file:
                    current_content = file.read()
                # Compare the content with the new value
                if current_content == request.json["value"]:
                    return make_response({"message": "No update needed. Content is the same as the current version."}, 200)
                new_version = version + 1
            else:
                return make_response({"message": "Configuration not found!"}, 404)

            # Check if the value exists in configuration_versions
            self.cur.execute("""
                SELECT id
                FROM configuration_versions
                WHERE value=%s
                AND id_configuration = %s
            """, (request.json["value"], id))
            existing_version = self.cur.fetchone()
            if existing_version is not None:
                return make_response({"message": "Version of configuration already exists"}, 400)

            # Mettre à jour la configuration actuelle avec la nouvelle version
            sql = """UPDATE configurations
                    SET value=%s,
                        updatedBy=%s,
                        description=%s,
                        version=%s
                    WHERE id=%s"""
            self.cur.execute(sql, (request.json["value"], profile_name, request.json["description"], new_version, id))
            self.conn.commit()

            # Insérer la nouvelle version de la configuration dans la table configuration_versions
            sql = """INSERT INTO configuration_versions (name, value, updatedBy, description, version, id_configuration, versionningAt)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id"""
            self.cur.execute(sql, (request.json["name"], request.json["value"], profile_name, request.json["description"], new_version, new_versionningAt, id))
            inserted_id = self.cur.fetchone()[0]
            self.conn.commit()

            updated_configurations = {
                "value": request.json["value"],
                "updatedBy": profile_name,
                "description": request.json["description"],
                "version": new_version,
                "versionningAt" : new_versionningAt
            }

            # Afficher les configurations actuelles
            self.cur.execute("SELECT * FROM configuration_versions")
            configurations = self.cur.fetchall()
            print(len(configurations))
            for configuration in configurations:
                print(configuration)

            return make_response(updated_configurations, 200)

        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error retrieving update configuration model: {e}"}, 500)



    def rollback_configuration(self, id):
        try:
            # Retrieve the current version from the configurations table
            sql = """SELECT version
                    FROM configurations
                    WHERE id = %s"""
            self.cur.execute(sql, (id,))
            current_version = self.cur.fetchone()

            if current_version is not None:
                current_version = current_version[0]  # Retrieve the current version

                if current_version > 1:
                    # Retrieve the closest previous version from the configuration_versions table
                    sql = """SELECT MAX(version) AS previous_version
                            FROM configuration_versions
                            WHERE id_configuration = %s AND version < %s"""
                    self.cur.execute(sql, (id, current_version))
                    previous_version = self.cur.fetchone()

                    if previous_version and previous_version[0] is not None:
                        previous_version = previous_version[0]

                        # Retrieve the previous version data from the configuration_versions table
                        sql = """SELECT name, value, updatedBy, description
                                FROM configuration_versions
                                WHERE id_configuration = %s AND version = %s"""
                        self.cur.execute(sql, (id, previous_version))
                        previous_version_data = self.cur.fetchone()

                        if previous_version_data is not None:
                            name, value, updated_by, description = previous_version_data

                            # Update the configuration with the previous version in the configurations table
                            sql = """UPDATE configurations
                                    SET name = %s, value = %s, updatedBy = %s, description = %s, version = %s
                                    WHERE id = %s"""
                            self.cur.execute(sql, (name, value, updated_by, description, previous_version, id))
                            self.conn.commit()

                            # Return the updated configuration
                            updated_configuration = {
                                "name": name,
                                "value": value,
                                "updatedBy": updated_by,
                                "description": description,
                                "version": previous_version
                            }
                            return make_response(updated_configuration, 200)
                        else:
                            return make_response({"message": "Previous version not found!"}, 404)
                    else:
                        return make_response({"message": "No previous version available!"}, 404)
                else:
                    return make_response({"message": "No previous version available!"}, 404)
            else:
                return make_response({"message": "Configuration not found!"}, 404)

        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error rolling back configuration: {e}"}, 500)


    def backup_configuration(self, id):
        try:
            # Retrieve the current version from the configurations table
            sql = """SELECT version
                    FROM configurations
                    WHERE id = %s"""
            self.cur.execute(sql, (id,))
            current_version = self.cur.fetchone()

            if current_version is not None:
                current_version = current_version[0]

                # Retrieve the closest next version from the configuration_versions table
                sql = """SELECT MIN(version) AS next_version
                        FROM configuration_versions
                        WHERE id_configuration = %s AND version > %s"""
                self.cur.execute(sql, (id, current_version))
                next_version = self.cur.fetchone()

                if next_version and next_version[0] is not None:
                    next_version = next_version[0]

                    # Retrieve the configuration data for the next version from configuration_versions table
                    sql = """SELECT name, value, updatedBy, description
                            FROM configuration_versions
                            WHERE id_configuration = %s AND version = %s"""
                    self.cur.execute(sql, (id, next_version))
                    configuration_data = self.cur.fetchone()

                    if configuration_data is not None:
                        name, value, updated_by, description = configuration_data

                        # Update the configuration in the configurations table with the next version
                        sql = """UPDATE configurations
                                SET name = %s, value = %s, updatedBy = %s, description = %s, version = %s
                                WHERE id = %s"""
                        self.cur.execute(sql, (name, value, updated_by, description, next_version, id))
                        self.conn.commit()

                        # Return the updated configuration
                        updated_configuration = {
                            "name": name,
                            "value": value,
                            "updatedBy": updated_by,
                            "description": description,
                            "version": next_version
                        }
                        return make_response(updated_configuration, 200)
                    else:
                        return make_response({"message": "Next version data not found!"}, 404)
                else:
                    return make_response({"message": "No next version found for the configuration!"}, 404)
            else:
                return make_response({"message": "Configuration not found!"}, 404)

        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error updating configuration: {e}"}, 500)
     
    def get_all_configurations_versions(self):
        try:
            self.cur.execute("SELECT * FROM configuration_versions ORDER BY id_configuration ASC, version ASC")
            self.conn.commit()
            configurations = [
                dict(
                    id=row[0],
                    name=row[1],
                    value=row[2],
                    updatedBy=row[3],
                    description=row[4],
                    version=row[5],
                    id_configuration=row[6],
                    versionningAt=row[7],  # Add versionningAt field
                )
                for row in self.cur.fetchall()
            ]
            if configurations:
                res = make_response(configurations, 200)
                res.headers['Access-Control-Allow-Origin'] = "*"
                return res
            else:
                return make_response({"message": "No configurations found!"}, 202)
        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error retrieving all configurations: {e}"}, 500)


    # def get_all_configurations_versions(self):
    #     try:
    #         self.cur.execute("SELECT * FROM configuration_versions ORDER BY id_configuration ASC, version ASC")
    #         self.conn.commit()
    #         configurations = [
    #             dict(id=row[0], name=row[1], value=row[2], updatedBy=row[3], description=row[4], version=row[5], id_configuration=row[6])
    #             for row in self.cur.fetchall()
    #         ]
    #         if configurations:
    #             res = make_response(configurations, 200)
    #             res.headers['Access-Control-Allow-Origin'] = "*"
    #             return res
    #         else:
    #             return make_response({"message": "No configurations found!"}, 202)
    #     except Exception as e:
    #         self.conn.rollback()
    #         return make_response({"message": f"Error retrieving all configurations: {e}"}, 500)


    def get_configuration_version(self, id):
        try:
            self.cur.execute("SELECT * FROM configuration_versions WHERE id=%s", (id,))
            row = self.cur.fetchone()
            if row is not None:
                configuration = dict(
                    id=row[0],
                    name=row[1],
                    value=row[2],
                    updatedBy=row[3],
                    description=row[4],
                    version=row[5],
                    id_configuration=row[6],
                    versionningAt=row[7],  # Add versionningAt field
                )
                return make_response(configuration, 200)
            else:
                return make_response({"message": "No configuration version found!"}, 202)
        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error retrieving configuration version: {e}"}, 500)
   
   
    def delete_configuration_version(self, id):
        try:
            # Check if the configuration version exists
            self.cur.execute("SELECT * FROM configuration_versions WHERE id = %s", (id,))
            configuration_version = self.cur.fetchone()

            if configuration_version:
                configuration_id = configuration_version[6]  # Get the corresponding configuration_id
                current_version = configuration_version[5]  # Get the current version

                # Check if this is the highest configuration version
                self.cur.execute("""
                    SELECT version
                    FROM configuration_versions
                    WHERE id_configuration = %s
                    ORDER BY version DESC
                    LIMIT 1
                """, (configuration_id,))
                highest_version = self.cur.fetchone()

                if highest_version and highest_version[0] == current_version:
                    # This is the highest version, perform rollback

                    # Retrieve the configuration data for the previous version
                    self.cur.execute("""
                        SELECT name, value, updatedBy, description, version
                        FROM configuration_versions
                        WHERE id_configuration = %s AND version < %s
                        ORDER BY version DESC
                        LIMIT 1
                    """, (configuration_id, current_version))
                    previous_version_data = self.cur.fetchone()

                    if previous_version_data:
                        previous_name, previous_value, previous_updated_by, previous_description, previous_version = previous_version_data

                        # Update the configuration with the previous version in the configurations table
                        self.cur.execute("""
                            UPDATE configurations
                            SET name = %s, value = %s, updatedBy = %s, description = %s, version = %s
                            WHERE id = %s
                        """, (previous_name, previous_value, previous_updated_by, previous_description, previous_version, configuration_id))
                        self.conn.commit()

                        # Delete the corresponding configuration version
                        self.cur.execute("DELETE FROM configuration_versions WHERE id = %s", (id,))
                        self.conn.commit()

                        logging.info(f"The configuration version with id: {id} has been deleted at {datetime.now()}")

                        # Return the updated configuration after rollback
                        updated_configuration = {
                            "name": previous_name,
                            "value": previous_value,
                            "updatedBy": previous_updated_by,
                            "description": previous_description,
                            "version": previous_version
                        }
                        res = make_response(updated_configuration, 200)
                        res.headers['Access-Control-Allow-Origin'] = "*"
                        return res
                    else:
                        return make_response({"message": "Previous version data not found!"}, 404)
                else:
                    # This is not the highest version, backup the configuration and delete the version

                    # Retrieve the configuration data for the next version
                    self.cur.execute("""
                        SELECT name, value, updatedBy, description, version
                        FROM configuration_versions
                        WHERE id_configuration = %s AND version > %s
                        ORDER BY version ASC
                        LIMIT 1
                    """, (configuration_id, current_version))
                    next_version_data = self.cur.fetchone()

                    if next_version_data:
                        next_name, next_value, next_updated_by, next_description, next_version = next_version_data

                        # Update the configuration with the next version in the configurations table
                        self.cur.execute("""
                            UPDATE configurations
                            SET name = %s, value = %s, updatedBy = %s, description = %s, version = %s
                            WHERE id = %s
                        """, (next_name, next_value, next_updated_by, next_description, next_version, configuration_id))
                        self.conn.commit()

                        # Delete the corresponding configuration version
                        self.cur.execute("DELETE FROM configuration_versions WHERE id = %s", (id,))
                        self.conn.commit()

                        logging.info(f"The configuration version with id: {id} has been deleted at {datetime.now()}")

                        # Return the updated configuration after deletion
                        updated_configuration = {
                            "name": next_name,
                            "value": next_value,
                            "updatedBy": next_updated_by,
                            "description": next_description,
                            "version": next_version
                        }
                        res = make_response(updated_configuration, 200)
                        res.headers['Access-Control-Allow-Origin'] = "*"
                        return res
                    else:
                        return make_response({"message": "Next version data not found!"}, 404)
            else:
                return make_response({"message": "Configuration version not found!"}, 404)
        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error deleting configuration version: {e}"}, 500)
