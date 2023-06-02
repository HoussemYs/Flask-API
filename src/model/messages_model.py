from app import app
from flask import request, make_response, json
import psycopg2
from db.database import connect
from datetime import datetime
import logging
import os


class messages():

    def __init__(self):
        try:
            self.conn, self.cur = connect()
        except psycopg2.Error as error:
            print(error)


    def get_all_conversations(self):
        try:
            self.cur.execute("SELECT * FROM conversations")
            conv = self.cur.fetchall()

            conversation_list = []
            for conversation in conv:
                conversation_data = {
                    "conversation_id": conversation[0],
                    "conversation_name": conversation[1],
                    "created_at": conversation[2]
                }
                conversation_list.append(conversation_data)

            if conversation_list:
                return make_response({"conversations": conversation_list}, 200)
            else:
                return make_response({"message": "No conversations found!"}, 404)
        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error retrieving conversations: {e}"}, 500)


    def get_all_messages(self, conversation_id):
        try:
            # Get conversation name
            self.cur.execute(
                """
                SELECT conversation_name FROM conversations WHERE conversation_id = %s
                """,
                (conversation_id,),
            )
            conversation_name_result = self.cur.fetchone()
            conversation_name = conversation_name_result[0] if conversation_name_result else "Unknown"

            self.cur.execute("""SELECT * FROM messages WHERE conversation_id = %s""", (conversation_id,))
            msgs = self.cur.fetchall()

            message_list = []
            for message in msgs:
                # Get sender's name
                sender_id = message[2]
                self.cur.execute(
                    """
                    SELECT name FROM profiles WHERE user_id = %s
                    """,
                    (sender_id,),
                )
                sender_name_result = self.cur.fetchone()
                sender_name = sender_name_result[0] if sender_name_result else "Unknown"

                # Get recipient's name
                recipient_id = message[5]
                self.cur.execute(
                    """
                    SELECT name FROM profiles WHERE user_id = %s
                    """,
                    (recipient_id,),
                )
                recipient_name_result = self.cur.fetchone()
                recipient_name = recipient_name_result[0] if recipient_name_result else "Unknown"

                message_data = {
                    "message_id": message[0],
                    "conversation_id": message[1],
                    "sender_id": message[2],
                    "sender_name": sender_name,
                    "content": message[3],
                    "timestamp": message[4],
                    "recipient_id": message[5],
                    "recipient_name": recipient_name
                }
                message_list.append(message_data)

            if message_list:
                sorted_messages = sorted(message_list, key=lambda x: x['timestamp'])
                response_payload = {
                    "conversation_name": conversation_name,
                    "conversation_messages": sorted_messages
                }
                return make_response(response_payload, 200)
            else:
                return make_response({"message": f"No messages found for this conversation with id: {conversation_id}!"}, 404)
        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error retrieving messages: {e}"}, 500)



    def create_conversation(self, sender_id, recipient_id, conversation_name):
        try:
            # Check if sender_id and recipient_id exist in the users table
            self.cur.execute("SELECT id FROM users WHERE id = %s", (sender_id,))
            sender_exists = self.cur.fetchone()
            
            if not sender_exists:
                return make_response({"message": "Invalid sender_id"}, 400)
            
            self.cur.execute("SELECT id FROM users WHERE id = %s", (recipient_id,))
            recipient_exists = self.cur.fetchone()
            
            if not recipient_exists:
                return make_response({"message": "Invalid recipient_id"}, 400)
            
            # Get the current timestamp
            timestamp = datetime.now()
            
            # Insert the conversation into the databasea
            self.cur.execute("""
                INSERT INTO conversations (conversation_name, created_at)
                VALUES (%s, %s)
                RETURNING conversation_id
            """, (conversation_name, timestamp))
            
            conversation_id = self.cur.fetchone()[0]
            self.conn.commit()
            
            return make_response({"conversation_id": conversation_id}, 200)
        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error creating conversation: {e}"}, 500)


    def create_message(self, conversation_id, sender_id, recipient_id, content):
        try:
            # Check if sender_id exists in the users table
            self.cur.execute("SELECT id FROM users WHERE id = %s", (sender_id,))
            sender_exists = self.cur.fetchone()

            if not sender_exists:
                return make_response({"message": "Invalid sender_id"}, 400)

            # Check if recipient_id exists in the users table
            self.cur.execute("SELECT id FROM users WHERE id = %s", (recipient_id,))
            recipient_exists = self.cur.fetchone()

            if not recipient_exists:
                return make_response({"message": "Invalid recipient_id"}, 400)

            if sender_id not in sender_exists:
                return make_response({"message": "Invalid sender_id"}, 400)
            if recipient_id not in recipient_exists:
                return make_response({"message": "Invalid recipient_id"}, 400)

            # Check if content is empty
            if not content:
                return make_response({"message": "Empty content"}, 400)
            
            # Check if sender_id exists in the users table
            self.cur.execute("SELECT conversation_id FROM conversations WHERE conversation_id = %s", (conversation_id,))
            conversation_exists = self.cur.fetchone()

            if not conversation_exists:
                return make_response({"message": "Invalid conversation_id"}, 400)

            # Get the current timestamp
            timestamp = datetime.now()

            # Insert the message into the database
            self.cur.execute("""
                INSERT INTO messages (conversation_id, sender_id, recipient_id, content, timestamp)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING message_id
            """, (conversation_id, sender_id, recipient_id, content, timestamp))

            message_id = self.cur.fetchone()[0]
            self.conn.commit()

            return make_response({"message_id": message_id}, 200)
        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error creating message: {e}"}, 500)


        
    
    def get_conversations(self, user_id):
        try:
            # Retrieve the list of conversations for a user
            self.cur.execute("""
                SELECT DISTINCT conversation_id
                FROM messages
                WHERE sender_id = %s
                UNION
                SELECT DISTINCT conversation_id
                FROM messages
                WHERE recipient_id = %s
            """, (user_id, user_id))

            conversation_ids = [row[0] for row in self.cur.fetchall()]

            
            # Retrieve all attributes from conversations for the conversation IDs
            conversations = []
            if conversation_ids:
                placeholders = ','.join(['%s'] * len(conversation_ids))
                self.cur.execute(f"""
                    SELECT *
                    FROM conversations
                    WHERE conversation_id IN ({placeholders})
                """, conversation_ids)
                rows = self.cur.fetchall()
                
                for row in rows:
                    conversation_id, conversation_name, created_at = row
                    created_at_formatted = created_at.strftime("%a, %d %b %Y %H:%M:%S GMT")
                    conversation_data = {
                        "conversation_id": conversation_id,
                        "conversation_name": conversation_name,
                        "created_at": created_at_formatted
                    }
                    conversations.append(conversation_data)

            return make_response({"conversations": conversations}, 200)
        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error retrieving conversations: {e}"}, 500)


    def get_messages(self, conversation_id):
        try:
            # Retrieve the messages for a conversation
            self.cur.execute("""
                SELECT message_id, sender_id, recipient_id, content, timestamp
                FROM messages
                WHERE conversation_id = %s
                ORDER BY timestamp ASC
            """, (conversation_id,))

            messages = []
            rows = self.cur.fetchall()
            for row in rows:
                message_id, sender_id, recipient_id, content, timestamp = row
                timestamp_formatted = timestamp.strftime("%a, %d %b %Y %H:%M:%S GMT")
                
                # Retrieve sender_name
                self.cur.execute("""
                    SELECT name
                    FROM profiles
                    WHERE user_id = %s
                """, (sender_id,))
                sender_name_row = self.cur.fetchone()
                sender_name = sender_name_row[0] if sender_name_row else "Unknown"
                
                message = {
                    "message_id": message_id,
                    "sender_id": sender_id,
                    "sender_name": sender_name,
                    "recipient_id": recipient_id,
                    "content": content,
                    "timestamp": timestamp_formatted
                }
                messages.append(message)

            # Retrieve conversation details
            self.cur.execute("""
                SELECT conversation_id, conversation_name, created_at
                FROM conversations
                WHERE conversation_id = %s
            """, (conversation_id,))
            conversation_row = self.cur.fetchone()
            conversation_id, conversation_name, created_at = conversation_row

            response_payload = {
                "conversation_id": conversation_id,
                "conversation_name": conversation_name,
                "created_at": created_at.strftime("%a, %d %b %Y %H:%M:%S GMT"),
                "conversation_messages": messages
            }

            return make_response(response_payload, 200)
        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error retrieving messages: {e}"}, 500)


        
    def mark_message_as_read(self, message_id):
        try:
            # Update the message as read in the database
            self.cur.execute("""
                UPDATE messages
                SET is_read = TRUE
                WHERE message_id = %s
            """, (message_id,))
            
            self.conn.commit()
            
            return make_response({"message": "Message marked as read"}, 200)
        except Exception as e:
            self.conn.rollback()
            return make_response({"message": f"Error marking message as read: {e}"}, 500)
