from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from config import Config
from extensions import db
from markupsafe import Markup

# Import blueprints
from routes.statute_routes import statute_bp
from routes.hierarchy_routes import hierarchy_bp
from routes.annotation_routes import annotation_bp
from routes.schedule_routes import schedule_bp

def create_app(config_class=Config):
    """Initialize the Flask application"""
    # Set up Flask app
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize database with the app
    db.init_app(app)
    
    # Register blueprints
    app.register_blueprint(statute_bp)
    app.register_blueprint(hierarchy_bp)
    app.register_blueprint(annotation_bp)
    app.register_blueprint(schedule_bp)
    
    # Home route
    @app.route('/')
    def index():
        # Get recent statutes for display on homepage
        recent_statutes = db.session.query(db.metadata.tables['statute']).order_by(
            db.metadata.tables['statute'].c.created_at.desc()
        ).limit(5).all()
        
        return render_template('index.html', recent_statutes=recent_statutes)


    # Define the filter
    def nl2br(value):
        return Markup(value.replace('\n', '<br>\n'))

    # Register the filter
    app.jinja_env.filters['nl2br'] = nl2br
    
    # Configure error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404
    
    @app.errorhandler(500)
    def server_error(e):
        return render_template('500.html'), 500
    
    # Template context processors
    @app.context_processor
    def inject_current_year():
        return dict(current_year=datetime.now().year)
    
    return app

app = create_app()

if __name__ == '__main__':
    # Create application instance
    
    # Run the application
    app.run(host='0.0.0.0', port=5000, debug=app.config['DEBUG'])