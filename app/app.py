from flask import Flask, jsonify, render_template
from flask_cors import CORS
from app.routes.api import api
from app.routes.swagger import swagger_json, swaggerui_blueprint
from app.config import DEBUG, SECRET_KEY, PORT

def create_app():
    """Create and configure the Flask application"""
    app = Flask(__name__)
    
    # Configure app
    app.config.update(
        SECRET_KEY=SECRET_KEY,
        DEBUG=DEBUG
    )
    
    # Enable CORS
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(api, url_prefix='/api')
    app.register_blueprint(swagger_json, url_prefix='/api')
    app.register_blueprint(swaggerui_blueprint)
    
    # Root route - can be used for health check
    @app.route('/')
    def index():
        return jsonify({
            "status": "ok",
            "message": "St. Gallen Management Model API is running",
            "documentation": "/api/docs"
        })
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "error": "Not found",
            "message": "The requested resource could not be found"
        }), 404
    
    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            "error": "Internal server error",
            "message": "An unexpected error occurred"
        }), 500
    
    return app

# Create the app instance
app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT) 