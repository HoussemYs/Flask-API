import logging
from flask import Flask, Blueprint
from flask_swagger_ui import get_swaggerui_blueprint
from flask_cors import CORS


app = Flask(__name__)
CORS(app, supports_credentials=True, origins='*')

# Set log level to INFO
# logging.basicConfig(filename='api.log', level=logging.INFO)

# Disable Flask and Werkzeug default loggers
# werkzeug_logger = logging.getLogger('werkzeug')
# werkzeug_logger.setLevel(logging.ERROR)
# app.logger.disabled = True

# from controller.profiles_controller import *
# from controller.users_controller import *
# from controller.roles_permissions_controller import *




from controller import *
