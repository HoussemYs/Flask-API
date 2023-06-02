from app import app
from model.messages_model import messages
from model.auth_model import auth_model
from flask import request, make_response
import traceback
from datetime import datetime

obj = messages()
auth = auth_model()

@app.route("/conversations", methods=["POST"])
def create_conversation():
    sender_id = request.json["sender_id"]
    recipient_id = request.json["recipient_id"]
    conversation_name = request.json["conversation_name"]
    
    result = obj.create_conversation(sender_id, recipient_id, conversation_name)
    
    return result

@app.route("/conversations", methods=["GET"])
# @auth.token_auth()
def get_all_conversations():
    try:
        response = obj.get_all_conversations()
        return response
    except Exception as e:
        traceback.print_exc()
        return make_response(f"Error getting conversations: {e}", 500)

@app.route("/conversation_messages/<conversation_id>", methods=["GET"])
# @auth.token_auth()
def get_all_messages(conversation_id):
    try:
        response = obj.get_all_messages(conversation_id)
        return response
    except Exception as e:
        traceback.print_exc()
        return make_response(f"Error getting messages: {e}", 500)

@app.route("/messages", methods=["POST"])
# @auth.token_auth()
def send_message():
    try:
        sender_id = request.json["sender_id"]
        recipient_id = request.json["recipient_id"]
        content = request.json["content"]
        conversation_id = request.json["conversation_id"]

        response = obj.create_message(conversation_id, sender_id, recipient_id, content)
        return response
    except Exception as e:
        traceback.print_exc()
        return make_response(f"Error sending message: {e}", 500)

@app.route("/conversations/<user_id>", methods=["GET"])
# @auth.token_auth()
def get_conversations(user_id):
    try:
        response = obj.get_conversations(user_id)
        return response
    except Exception as e:
        traceback.print_exc()
        return make_response(f"Error retrieving conversations: {e}", 500)


@app.route("/messages/<conversation_id>", methods=["GET"])
# @auth.token_auth()
def get_messages(conversation_id):
    try:
        response = obj.get_messages(conversation_id)
        return response
    except Exception as e:
        traceback.print_exc()
        return make_response(f"Error retrieving messages: {e}", 500)

@app.route("/messages/read/<message_id>", methods=["PUT"])
# @auth.token_auth()
def mark_message_as_read(message_id):
    try:
        response = obj.mark_message_as_read(message_id)
        return response
    except Exception as e:
        traceback.print_exc()
        return make_response(f"Error marking message as read: {e}", 500)
