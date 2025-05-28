from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app
from sqlalchemy.exc import SQLAlchemyError
from models import db, Statute
from forms import StatuteForm
from database import check_exists, save_with_transaction, get_full_hierarchy
from datetime import datetime
import pytz

statute_bp = Blueprint('statute', __name__, url_prefix='/statute')

@statute_bp.route('/', methods=['GET'])
def list_statutes():
    """List all statutes"""
    try:
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = current_app.config.get('STATUTES_PER_PAGE', 10)
        
        # Get search parameter
        search = request.args.get('search', '')
        
        # Query statutes
        query = db.session.query(Statute)
        
        # Apply search filter if provided
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (Statute.name.ilike(search_term)) | 
                (Statute.act_no.ilike(search_term))
            )
        
        # Order by recently updated
        query = query.order_by(Statute.updated_at.desc())
        
        # Paginate results
        statutes = query.paginate(page=page, per_page=per_page)
        
        return render_template('statute/list.html', statutes=statutes, search=search)
    except Exception as e:
        current_app.logger.error(f"Error listing statutes: {str(e)}")
        flash("An error occurred while retrieving statutes.", "danger")
        return redirect(url_for('index'))

@statute_bp.route('/new', methods=['GET', 'POST'])
def add_statute():
    """Add a new statute"""
    form = StatuteForm()
    
    if request.method == 'POST' and form.validate_on_submit():
        try:
            # Check if statute with same name already exists
            existing = check_exists(Statute, name=form.name.data)
            if existing:
                flash(f"A statute with the name '{form.name.data}' already exists.", "danger")
                return render_template('statute/add.html', form=form)
            
            # Create new statute
            statute = Statute(
                name=form.name.data,
                act_no=form.act_no.data,
                date=form.date.data,
                preface=form.preface.data,
                created_at=datetime.now(pytz.UTC),
                updated_at=datetime.now(pytz.UTC)
            )
            
            # Save the statute
            success, message = save_with_transaction(statute)
            
            if success:
                flash(f"Statute '{statute.name}' created successfully!", "success")
                
                # Determine next action based on form button
                action = request.form.get('action', 'save')
                if action == 'save_and_add_part':
                    return redirect(url_for('hierarchy.add_part', statute_id=statute.id))
                else:
                    return redirect(url_for('statute.view_statute', statute_id=statute.id))
            else:
                flash(message, "danger")
        except Exception as e:
            current_app.logger.error(f"Error adding statute: {str(e)}")
            flash("An error occurred while creating the statute.", "danger")
    
    return render_template('statute/add.html', form=form)

@statute_bp.route('/<int:statute_id>', methods=['GET'])
def view_statute(statute_id):
    """View details of a statute"""
    try:
        # Get the statute
        statute = db.session.query(Statute).filter(Statute.id == statute_id).first()
        
        if not statute:
            flash("Statute not found.", "danger")
            return redirect(url_for('statute.list_statutes'))
        
        # Get the full hierarchy for this statute
        hierarchy = get_full_hierarchy(statute_id)
        from pprint import pprint
        pprint(hierarchy)
        
        return render_template(
            'statute/view.html', 
            statute=statute, 
            parts=hierarchy.get('parts', []) if hierarchy else [],
            sch_parts=hierarchy.get('sch_parts', []) if hierarchy else []
        )
    except Exception as e:
        current_app.logger.error(f"Error viewing statute: {str(e)}")
        flash("An error occurred while retrieving the statute.", "danger")
        return redirect(url_for('statute.list_statutes'))

@statute_bp.route('/<int:statute_id>/edit', methods=['GET', 'POST'])
def edit_statute(statute_id):
    """Edit an existing statute"""
    try:
        # Get the statute
        statute = db.session.query(Statute).filter(Statute.id == statute_id).first()
        
        if not statute:
            flash("Statute not found.", "danger")
            return redirect(url_for('statute.list_statutes'))
        
        # Create form and populate with existing data
        form = StatuteForm(obj=statute)
        
        if request.method == 'POST' and form.validate_on_submit():
            # Check if name change would create a duplicate
            if form.name.data != statute.name:
                existing = check_exists(Statute, name=form.name.data)
                if existing and existing.id != statute.id:
                    flash(f"A statute with the name '{form.name.data}' already exists.", "danger")
                    return render_template('statute/edit.html', form=form, statute=statute)
            
            # Update statute
            statute.name = form.name.data
            statute.act_no = form.act_no.data
            statute.date = form.date.data
            statute.preface = form.preface.data
            statute.updated_at = datetime.now(pytz.UTC)
            
            # Save the changes
            success, message = save_with_transaction(statute)
            
            if success:
                flash(f"Statute '{statute.name}' updated successfully!", "success")
                return redirect(url_for('statute.view_statute', statute_id=statute.id))
            else:
                flash(message, "danger")
        
        return render_template('statute/edit.html', form=form, statute=statute)
    except Exception as e:
        current_app.logger.error(f"Error editing statute: {str(e)}")
        flash("An error occurred while editing the statute.", "danger")
        return redirect(url_for('statute.list_statutes'))

@statute_bp.route('/<int:statute_id>/delete', methods=['POST'])
def delete_statute(statute_id):
    """Delete a statute and all its components"""
    try:
        # Get the statute
        statute = db.session.query(Statute).filter(Statute.id == statute_id).first()
        
        if not statute:
            flash("Statute not found.", "danger")
            return redirect(url_for('statute.list_statutes'))
        
        # Store name for flash message
        statute_name = statute.name
        
        # Delete the statute (cascade will delete all children)
        db.session.delete(statute)
        db.session.commit()
        
        flash(f"Statute '{statute_name}' and all its components have been deleted.", "success")
        return redirect(url_for('statute.list_statutes'))
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Database error deleting statute: {str(e)}")
        flash("A database error occurred while deleting the statute.", "danger")
        return redirect(url_for('statute.list_statutes'))
    except Exception as e:
        current_app.logger.error(f"Error deleting statute: {str(e)}")
        flash("An error occurred while deleting the statute.", "danger")
        return redirect(url_for('statute.list_statutes'))