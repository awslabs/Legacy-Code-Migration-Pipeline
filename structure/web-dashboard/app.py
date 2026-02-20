#!/usr/bin/env python3
"""
Migration Dashboard - Flask Application (Refactored)

A web-based dashboard for monitoring COBOL to Java migration progress.
"""

from flask import Flask
from config import config
from models.data_loader import MigrationDataLoader
from routes.main_routes import main_bp
from routes.api_routes import api_bp
from routes.admin_routes import admin_bp

def create_app(config_name='default'):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize data loader
    data_loader = MigrationDataLoader()
    
    # Make data_loader available to blueprints
    app.data_loader = data_loader
    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(admin_bp)
    
    return app

if __name__ == '__main__':
    import os
    config_name = os.environ.get('FLASK_CONFIG', 'default')
    app = create_app(config_name)
    
    app.run(
        host=app.config['HOST'],
        port=app.config['PORT'],
        debug=app.config['DEBUG']
    )