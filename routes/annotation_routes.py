from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from sqlalchemy.exc import SQLAlchemyError
from extensions import db
from models import Annotation, Statute
from forms import AnnotationForm
from database import save_with_transaction
from datetime import datetime
import pytz

annotation_bp = Blueprint('annotation', __name__, url_prefix='/annotation')

@annotation_bp.route('/statute/<int:statute_id>/new', methods=['GET', 'POST'])
def add_annotation(statute_id):
    """Add a new annotation to a statute"""
    # Get the statute
    statute = db.session.query(Statute).filter(Statute.id == statute_id).first()
    if not statute:
        flash("Statute not found.", "danger")
        return redirect(url_for('statute.list_statutes'))
    
    # Create form
    form = AnnotationForm()
    form.statute_id.data = statute_id
    
    if request.method == 'POST' and form.validate_on_submit():
        try:
            # Create new annotation
            annotation = Annotation(
                no=form.no.data,
                statute_id=form.statute_id.data,
                page_no=form.page_no.data,
                footnote=form.footnote.data,
                created_at=datetime.now(pytz.UTC),
                updated_at=datetime.now(pytz.UTC)
            )
            
            # Save the annotation
            success, message = save_with_transaction(annotation)
            
            if success:
                flash(f"Annotation '{annotation.no}' added successfully!", "success")
                
                # Determine next action based on form button
                action = request.form.get('action', 'save')
                if action == 'save_and_add_another':
                    return redirect(url_for('annotation.add_annotation', statute_id=statute_id))
                else:
                    # Return to statute view
                    return redirect(url_for('statute.view_statute', statute_id=statute_id))
            else:
                flash(message, "danger")
                
        except Exception as e:
            current_app.logger.error(f"Error adding annotation: {str(e)}")
            flash("An error occurred while creating the annotation.", "danger")
    
    # For GET request or failed POST, show the form
    return render_template('annotation/add.html', form=form, statute=statute)

@annotation_bp.route('/<int:annotation_id>/edit', methods=['GET', 'POST'])
def edit_annotation(annotation_id):
    """Edit an existing annotation"""
    try:
        # Get the annotation
        annotation = db.session.query(Annotation).filter(Annotation.id == annotation_id).first()
        
        if not annotation:
            flash("Annotation not found.", "danger")
            return redirect(url_for('annotation.list_annotations'))
        
        # Get the statute
        statute = db.session.query(Statute).filter(Statute.id == annotation.statute_id).first()
        
        # Create form and populate with existing data
        form = AnnotationForm(obj=annotation)
        
        if request.method == 'POST' and form.validate_on_submit():
            # Update annotation
            annotation.no = form.no.data
            annotation.page_no = form.page_no.data
            annotation.footnote = form.footnote.data
            annotation.updated_at = datetime.now(pytz.UTC)
            
            # Save the changes
            success, message = save_with_transaction(annotation)
            
            if success:
                flash(f"Annotation '{annotation.no}' updated successfully!", "success")
                
                # Return to statute view
                return redirect(url_for('statute.view_statute', statute_id=annotation.statute_id))
            else:
                flash(message, "danger")
                
        
        # For GET request or failed POST, show the form
        return render_template('annotation/edit.html', form=form, annotation=annotation, statute=statute)
    except Exception as e:
        current_app.logger.error(f"Error editing annotation: {str(e)}")
        flash("An error occurred while editing the annotation.", "danger")
        return redirect(url_for('annotation.list_annotations'))

@annotation_bp.route('/<int:annotation_id>/delete', methods=['POST'])
def delete_annotation(annotation_id):
    """Delete an annotation"""
    try:
        # Get the annotation
        annotation = db.session.query(Annotation).filter(Annotation.id == annotation_id).first()
        
        if not annotation:
            flash("Annotation not found.", "danger")
            
            return redirect(url_for('annotation.list_annotations'))
        
        # Store annotation number and statute ID for redirect
        annotation_no = annotation.no
        statute_id = annotation.statute_id
        
        # Delete the annotation
        db.session.delete(annotation)
        db.session.commit()
        
        flash(f"Annotation '{annotation_no}' has been deleted.", "success")
        
        # Redirect to statute view
        return redirect(url_for('statute.view_statute', statute_id=statute_id))
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Database error deleting annotation: {str(e)}")
        flash("A database error occurred while deleting the annotation.", "danger")
        
        return redirect(url_for('annotation.list_annotations'))
    except Exception as e:
        current_app.logger.error(f"Error deleting annotation: {str(e)}")
        flash("An error occurred while deleting the annotation.", "danger")
        
        return redirect(url_for('annotation.list_annotations'))

@annotation_bp.route('/statute/<int:statute_id>/list', methods=['GET'])
def list_statute_annotations(statute_id):
    """List all annotations for a specific statute"""
    try:
        # Get the statute
        statute = db.session.query(Statute).filter(Statute.id == statute_id).first()
        if not statute:
            flash("Statute not found.", "danger")
            return redirect(url_for('statute.list_statutes'))
        
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = current_app.config.get('ANNOTATIONS_PER_PAGE', 20)
        
        # Get search parameter
        search = request.args.get('search', '')
        
        # Query annotations for this statute
        query = db.session.query(Annotation).filter(Annotation.statute_id == statute_id)
        
        # Apply search filter if provided
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (Annotation.no.ilike(search_term)) | 
                (Annotation.page_no.ilike(search_term)) |
                (Annotation.footnote.ilike(search_term))
            )
        
        # Order by number
        query = query.order_by(Annotation.no)
        
        # Paginate results
        annotations = query.paginate(page=page, per_page=per_page)
        
        return render_template('annotation/list.html', annotations=annotations, search=search, statute=statute)
    except Exception as e:
        current_app.logger.error(f"Error listing annotations: {str(e)}")
        flash("An error occurred while retrieving annotations.", "danger")
        return redirect(url_for('statute.view_statute', statute_id=statute_id))

@annotation_bp.route('/list', methods=['GET'])
def list_annotations():
    """List all annotations across all statutes"""
    try:
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = current_app.config.get('ANNOTATIONS_PER_PAGE', 20)
        
        # Get search parameter
        search = request.args.get('search', '')
        
        # Query annotations
        query = db.session.query(Annotation)
        
        # Apply search filter if provided
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (Annotation.no.ilike(search_term)) | 
                (Annotation.page_no.ilike(search_term)) |
                (Annotation.footnote.ilike(search_term))
            )
        
        # Order by number
        query = query.order_by(Annotation.no)
        
        # Paginate results
        annotations = query.paginate(page=page, per_page=per_page)
        
        return render_template('annotation/list.html', annotations=annotations, search=search)
    except Exception as e:
        current_app.logger.error(f"Error listing annotations: {str(e)}")
        flash("An error occurred while retrieving annotations.", "danger")
        return redirect(url_for('index'))

    """API endpoint for saving annotations via AJAX"""
    form = AnnotationForm(request.form)
    
    if form.validate():
        try:
            # Check if editing existing annotation
            annotation_id = request.form.get('id')
            
            if annotation_id:
                # Get existing annotation
                annotation = db.session.query(Annotation).filter(Annotation.id == annotation_id).first()
                
                if not annotation:
                    return jsonify({'success': False, 'message': "Annotation not found."})
                
                # Update annotation
                annotation.no = form.no.data
                annotation.page_no = form.page_no.data
                annotation.footnote = form.footnote.data
                annotation.updated_at = datetime.now(pytz.UTC)
            else:
                # Create new annotation
                annotation = Annotation(
                    no=form.no.data,
                    statute_id=form.statute_id.data,
                    page_no=form.page_no.data,
                    footnote=form.footnote.data,
                    created_at=datetime.now(pytz.UTC),
                    updated_at=datetime.now(pytz.UTC)
                )
            
            # Save the annotation
            success, message = save_with_transaction(annotation)
            
            if success:
                return jsonify({
                    'success': True, 
                    'message': f"Annotation '{annotation.no}' saved successfully!",
                    'annotation': {
                        'id': annotation.id,
                        'no': annotation.no,
                        'statute_id': annotation.statute_id,
                        'page_no': annotation.page_no,
                        'footnote': annotation.footnote
                    }
                })
            else:
                return jsonify({'success': False, 'message': message})
        except Exception as e:
            current_app.logger.error(f"Error saving annotation via API: {str(e)}")
            return jsonify({'success': False, 'message': "An error occurred while saving the annotation."})
    else:
        # Form validation failed
        errors = []
        for field, field_errors in form.errors.items():
            errors.append(f"{field}: {', '.join(field_errors)}")
        
        return jsonify({'success': False, 'message': "Validation failed.", 'errors': errors})