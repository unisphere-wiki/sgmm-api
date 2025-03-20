from flask import Blueprint, jsonify
from flask_swagger_ui import get_swaggerui_blueprint
from app.swagger import get_swagger_spec

# Create a Blueprint for the Swagger JSON endpoint
swagger_json = Blueprint('swagger_json', __name__)

# Create the SwaggerUI Blueprint
SWAGGER_URL = '/api/docs'  # URL for accessing the Swagger UI
API_URL = '/api/swagger.json'  # URL for the Swagger JSON

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "St. Gallen Management Model API"
    }
)

@swagger_json.route('/swagger.json', methods=['GET'])
def swagger_spec():
    """Returns the Swagger specification JSON"""
    return jsonify(get_swagger_spec()) 