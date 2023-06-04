

# ************************CODE DESCRIPTION PROFILES_MODEL************************

    # all Functions get requests from controller : check the token and if he have permission he can access to function

        # Function add_profile : get the profile informations : name, email, telephone, adresse, image, description, user_id passed from client-side
                        # and then save the profile with the user_id to affect the profile to the user who have this user_id
        # Function update_profile : get the profile informations passed from client-side
                        # and make the updates of the profile who have the id passed in path
        # Function delete_profile : get the id in path for the profile that will be deleted
                        # and make the delete of the profile who have the id passed in path
        # Function get_profile : get the id in path for the profile searched
                        # and get the profile who have the id=id_passed 
        # Function get_all_profiles : get all profiles with the informations : id, name, email, telephone, adresse, image, description, user_id 
        # Function upload_image_file : get the image passed in the client-side and cript the name with thisTime to be all the images names are differents
        # Function get_image_by_id : get the id of profile in path passed from client-side 
                        # then get the image of profile who have that id passed


from app import app
from flask import request, make_response, send_file , json
import psycopg2
from io import BytesIO
from db.database import connect
import os
import jwt

class profiles():
    def __init__(self):
        try:
            self.conn, self.cur = connect()
        except psycopg2.Error as error:
            print(error)

    
    def search_profiles(self, term):
        try:
            self.cur.execute("SELECT * FROM profiles WHERE name ILIKE %s ORDER BY id ASC", ('%' + term + '%',))
            profiles = [
                {
                    "id": row[0],
                    "name": row[1],
                    "email": row[2],
                    "telephone": row[3],
                    "adresse": row[4],
                    "image": row[5],
                    "description": row[6],
                    "user_id": row[7]
                }
                for row in self.cur.fetchall()
            ]
            
            if profiles:
                return make_response(profiles, 200)
            else:
                return make_response({"message": "No profiles found!"}, 202)
        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error retrieving profiles: {e}"}, 500)
        
                
    def add_profile(self, data):
        try:
            data_str = data.decode('utf-8')
            data_dict = json.loads(data_str)

            token = request.headers.get("Authorization", "").split(" ")[-1]
            jwtdecoded = jwt.decode(token, "HoussemYousfi", algorithms="HS256")
            new_user_id = jwtdecoded["user_id"]
        
            new_name = data_dict['name']
            new_email = data_dict['email']
            new_telephone = data_dict['telephone']
            new_adresse = data_dict['adresse']
            new_image = data_dict['image']
            new_description = data_dict['description']
            
            sql = """INSERT INTO profiles (name, email, telephone, adresse, image, description, user_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            self.cur.execute(sql, (new_name, new_email, new_telephone,
                                new_adresse, new_image, new_description, new_user_id))
            self.conn.commit()
            self.cur.execute(
                "SELECT currval(pg_get_serial_sequence('profiles', 'id'));")
            profile_id = self.cur.fetchone()[0]
            res = dict(message=f"Profile with the id: {profile_id} created successfully", id=profile_id )
            return make_response(res, 201)
        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error retrieving add profile : {e}"}, 500)

    def get_profile(self, id):
        try:
            self.cur.execute("SELECT * FROM profiles WHERE id=%s", (id,))
            row = self.cur.fetchone()
            if row is not None:
                profile = dict(id=row[0], name=row[1], email=row[2], telephone=row[3],
                               adresse=row[4], image=row[5], description=row[6], user_id=row[7])
                res = make_response(profile, 200)
                res.headers['Access-Control-Allow-Origin'] = "*"
                return res
            else:
                return make_response({"message": "No profile found !"}, 202)
        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error retrieving get profile : {e}"}, 500)

    def get_all_profiles(self):
        try:
            self.cur.execute("SELECT * FROM profiles")
            self.conn.commit()
            profiles = [
                dict(id=row[0], name=row[1], email=row[2], telephone=row[3],
                     adresse=row[4], image=row[5], description=row[6], user_id=row[7])
                for row in self.cur.fetchall()
            ]
            if profiles is not None:
                res = make_response(profiles, 200)
                res.headers['Access-Control-Allow-Origin'] = "*"
                return res
            else:
                return make_response({"message": "No profiles found !"}, 202)
        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error retrieving get all profiles : {e}"}, 500)

    
    def update_profile(self, id, data):
        try:
            data_str = data.decode('utf-8')
            data_dict = json.loads(data_str)
            
            current_name = data_dict['name']
            current_email = data_dict['email']
            current_telephone = data_dict['telephone']
            current_adresse = data_dict['adresse']
            current_description = data_dict['description']
            sql = """UPDATE profiles
                    SET name=%s,
                        email=%s,
                        telephone=%s,
                        adresse=%s,
                        description=%s
                    WHERE id=%s"""
            self.cur.execute(sql, (current_name, current_email, current_telephone,
                                   current_adresse, current_description, id))
            self.conn.commit()
            # Return the updated profile
            updated_profile = {
                "name": current_name,
                "email": current_email,
                "telephone": current_telephone,
                "adresse": current_adresse,
                "description": current_description
            }
            if self.cur.rowcount > 0:
                return make_response(updated_profile, 201)
            else:
                return make_response({"message": "Nothing to Updated in update model"}, 202)
        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error retrieving update profile : {e}"}, 500)

    def delete_profile(self, id):
        try:
            self.cur.execute(f"DELETE from profiles WHERE id=%s", (id,))
            self.conn.commit()
            if self.cur.rowcount > 0:
                return make_response("Profile deleted Successfully", 200)
            else:
                return make_response("Nothing Deleted", 202)
        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error retrieving delete profile : {e}"}, 500)

    def getProfileByUserId(self, id): 
        try:
            self.cur.execute("SELECT * FROM profiles WHERE user_id=%s", (id,))
            row = self.cur.fetchone()
            if row is not None:
                profile = dict(id=row[0], name=row[1], email=row[2], telephone=row[3],
                               adresse=row[4], image=row[5], description=row[6], user_id=row[7])
                res = make_response(profile, 200)
                res.headers['Access-Control-Allow-Origin'] = "*"
                return res
            else:
                return make_response({"message": "No profile found !"}, 202)
        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error retrieving get profile : {e}"}, 500)


    # FILES HEREEEEE
    def profile_upload_image(self, uid, filepath):
        self.cur.execute(
            f"UPDATE profiles SET image='{filepath}' WHERE id=%s", (uid,))
        self.conn.commit()
        if self.cur.rowcount > 0:
            return make_response({"message": f"Profile image updated successfully with name : {filepath}!"}, 201)
        else:
            return make_response({"message": "Nothing done !!!!!!"}, 202)

    def get_image_by_id_profile(self, id):
        self.cur.execute("SELECT image FROM profiles WHERE id=%s", (id,))
        result = self.cur.fetchone()
        if result is not None:
            image_path = result[0]
            # return send_file(f"{image_path}")
            return f"{os.getcwd()}/{image_path}"
        else:
            return make_response({"message": "No image found for this profile!"}, 404)
