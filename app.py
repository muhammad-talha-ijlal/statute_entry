from flask import Flask, render_template
from datetime import datetime

from flask_login import login_required
from config import Config
from extensions import db
from markupsafe import Markup
import re
from extensions import db, login_manager  # import the new object
from models import User                   # needed by user_loader
# Import blueprints
from routes.statute_routes import statute_bp
from routes.hierarchy_routes import hierarchy_bp
from routes.annotation_routes import annotation_bp
from routes.schedule_routes import schedule_bp
from routes.auth_routes import auth_bp

def create_app(config_class=Config):
    """Initialize the Flask application"""
    # Set up Flask app
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize database with the app
    db.init_app(app)
    login_manager.init_app(app)               # NEW

    @login_manager.user_loader                # NEW
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Register blueprints
    app.register_blueprint(statute_bp)
    app.register_blueprint(hierarchy_bp)
    app.register_blueprint(annotation_bp)
    app.register_blueprint(schedule_bp)
    app.register_blueprint(auth_bp)

    # Session management for PostgreSQL + Gunicorn
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        """Ensure database sessions are properly closed"""
        try:
            if exception:
                db.session.rollback()
            db.session.remove()
        except Exception as e:
            app.logger.error(f"Error in session teardown: {e}")
    
    @app.before_request
    def before_request():
        """Ensure fresh database connection for each request"""
        try:
            # Test the connection
            db.session.execute(db.text('SELECT 1'))
        except Exception as e:
            app.logger.warning(f"Database connection issue, reconnecting: {e}")
            db.session.rollback()
            db.session.remove()
    
    # Home route
    @app.route('/')
    @login_required
    def index():
        # Get recent statutes for display on homepage
        recent_statutes = db.session.query(db.metadata.tables['statute']).order_by(
            db.metadata.tables['statute'].c.created_at.desc()
        ).limit(5).all()
        
        return render_template('index.html', recent_statutes=recent_statutes)

    # Define filters
    def nl2br(value):
        """Convert newlines to <br> tags"""
        if not value:
            return ''
        return Markup(value.replace('\n', '<br>\n'))
    
    def process_annotations_filter(text, statute_id=None):
        """
        Template filter to process annotation tags in text.
        This is a simplified version for template use.
        """
        if not text or not statute_id:
            return text
        
        # Import here to avoid circular imports
        from models import Annotation
        
        # Get annotations for this statute
        annotations = {}
        try:
            statute_annotations = db.session.query(Annotation).filter(
                Annotation.statute_id == statute_id
            ).all()
            
            for ann in statute_annotations:
                key = f"{ann.no}_{ann.page_no}" if ann.page_no else ann.no
                annotations[key] = ann.footnote
        except Exception as e:
            app.logger.error(f"Error fetching annotations: {str(e)}")
            return text
        
        processed_text = text
        
        # Pattern to match both fa and pa tags
        pattern = r'<(fa|pa)\s+a=([^>\s]+)(?:\s+p=([^>\s]+))?[^>]*>(.*?)</\1>'
        
        def replace_annotation(match):
            tag_type = match.group(1)  # 'fa' or 'pa'
            a_value = match.group(2)   # annotation number
            p_value = match.group(3)   # page number (optional)
            content = match.group(4)   # text content
            
            # Create annotation key
            ann_key = f"{a_value}_{p_value}" if p_value else a_value
            
            # Get footnote text
            footnote_text = annotations.get(ann_key, f"Annotation {a_value} not found")
            
            # Escape quotes for HTML attribute
            footnote_escaped = footnote_text.replace('"', '&quot;').replace("'", "&#39;")
            
            # Create formatted text with superscript and tooltip
            formatted = f'<span class="annotated-text" title="{footnote_escaped}" data-annotation="{a_value}"><sup class="annotation-number">{a_value}</sup>[{content}]</span>'
            
            return formatted
        
        # Process all annotation tags (handle nesting by processing innermost first)
        while re.search(pattern, processed_text, re.DOTALL):
            processed_text = re.sub(pattern, replace_annotation, processed_text, flags=re.DOTALL)
        
        return Markup(processed_text)

    # Register the filters
    app.jinja_env.filters['nl2br'] = nl2br
    app.jinja_env.filters['process_annotations'] = process_annotations_filter
    
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
    
    # Run the application
    app.run(host='0.0.0.0', port=5000, debug=app.config['DEBUG'])