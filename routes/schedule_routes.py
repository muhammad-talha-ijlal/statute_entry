from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app
from sqlalchemy.exc import SQLAlchemyError
from models import db, Statute, SchPart, SchChapter, SchSet, SchSection, SchSubsection
from forms import SchPartForm, SchChapterForm, SchSetForm, SchSectionForm, SchSubsectionForm
from database import save_with_transaction, get_next_order_no
from datetime import datetime
import pytz
from flask_login import login_required
schedule_bp = Blueprint('schedule', __name__, url_prefix='/schedule')

# Schedule Part routes
@schedule_bp.route('/statute/<int:statute_id>/part/new', methods=['GET', 'POST'])
@login_required
def add_sch_part(statute_id):
    """Add a new schedule part to a statute"""
    try:
        # Get the statute
        statute = db.session.query(Statute).filter(Statute.id == statute_id).first()
        if not statute:
            flash("Statute not found.", "danger")
            return redirect(url_for('statute.list_statutes'))
        
        # Create form
        form = SchPartForm()
        form.statute_id.data = statute_id
        
        if request.method == 'POST' and form.validate_on_submit():
            # Get next order number
            order_no = get_next_order_no(statute_id, SchPart, 'statute_id')
            
            # Create new schedule part
            sch_part = SchPart(
                statute_id=statute_id,
                name=form.name.data,
                part_no=form.part_no.data,
                order_no=order_no,
                created_at=datetime.now(pytz.UTC),
                updated_at=datetime.now(pytz.UTC)
            )
            
            # Save the schedule part
            success, message = save_with_transaction(sch_part)
            if success:
                flash(f"Schedule part '{sch_part.name}' added successfully.", "success")
                
                # Handle different actions
                action = request.form.get('action', 'save')
                if action == 'save_add_another':
                    return redirect(url_for('schedule.add_sch_part', statute_id=statute_id))
                elif action == 'save_add_chapter':
                    return redirect(url_for('schedule.add_sch_chapter', sch_part_id=sch_part.id))
                else:
                    return redirect(url_for('statute.view_statute', statute_id=statute_id))
            else:
                flash(message, "danger")
        
        
        return render_template(
            'schedule/add_part.html', 
            form=form, 
            statute=statute
        )
    except Exception as e:
        current_app.logger.error(f"Error adding schedule part: {str(e)}")
        flash("An error occurred while adding the schedule part.", "danger")
        return redirect(url_for('statute.view_statute', statute_id=statute_id))

@schedule_bp.route('/part/<int:sch_part_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_sch_part(sch_part_id):
    """Edit an existing schedule part"""
    try:
        # Get the schedule part
        sch_part = db.session.query(SchPart).filter(SchPart.id == sch_part_id).first()
        if not sch_part:
            flash("Schedule part not found.", "danger")
            return redirect(url_for('statute.list_statutes'))
        
        # Get the statute for breadcrumb
        statute = db.session.query(Statute).filter(Statute.id == sch_part.statute_id).first()
        
        # Create form and populate with existing data
        form = SchPartForm(obj=sch_part)
        
        if request.method == 'POST' and form.validate_on_submit():
            # Update schedule part
            sch_part.name = form.name.data
            sch_part.part_no = form.part_no.data
            sch_part.updated_at = datetime.now(pytz.UTC)
            
            # Save the changes
            success, message = save_with_transaction(sch_part)
            if success:
                flash(f"Schedule part '{sch_part.name}' updated successfully.", "success")
                return redirect(url_for('statute.view_statute', statute_id=sch_part.statute_id))
            else:
                flash(message, "danger")
        
        return render_template(
            'schedule/edit_part.html', 
            form=form, 
            sch_part=sch_part,
            statute=statute
        )
    except Exception as e:
        current_app.logger.error(f"Error editing schedule part: {str(e)}")
        flash("An error occurred while editing the schedule part.", "danger")
        return redirect(url_for('statute.list_statutes'))

@schedule_bp.route('/part/<int:sch_part_id>/delete', methods=['POST'])
@login_required
def delete_sch_part(sch_part_id):
    """Delete a schedule part and all its components"""
    try:
        # Get the schedule part
        sch_part = db.session.query(SchPart).filter(SchPart.id == sch_part_id).first()
        if not sch_part:
            flash("Schedule part not found.", "danger")
            return redirect(url_for('statute.list_statutes'))
        
        statute_id = sch_part.statute_id
        
        # Delete the schedule part (cascade will delete all children)
        db.session.delete(sch_part)
        db.session.commit()
        
        flash(f"Schedule part '{sch_part.name}' and all its components have been deleted.", "success")
        return redirect(url_for('statute.view_statute', statute_id=statute_id))
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Database error deleting schedule part: {str(e)}")
        flash("A database error occurred while deleting the schedule part.", "danger")
        return redirect(url_for('statute.list_statutes'))
    except Exception as e:
        current_app.logger.error(f"Error deleting schedule part: {str(e)}")
        flash("An error occurred while deleting the schedule part.", "danger")
        return redirect(url_for('statute.list_statutes'))

# Schedule Chapter routes
@schedule_bp.route('/part/<int:sch_part_id>/chapter/new', methods=['GET', 'POST'])
@login_required
def add_sch_chapter(sch_part_id):
    """Add a new schedule chapter to a part"""
    try:
        # Get the schedule part
        sch_part = db.session.query(SchPart).filter(SchPart.id == sch_part_id).first()
        if not sch_part:
            flash("Schedule part not found.", "danger")
            return redirect(url_for('statute.list_statutes'))
        
        # Get the statute for breadcrumb
        statute = db.session.query(Statute).filter(Statute.id == sch_part.statute_id).first()
        
        # Create form
        form = SchChapterForm()
        form.sch_part_id.data = sch_part_id
        
        if request.method == 'POST' and form.validate_on_submit():
            # Get next order number
            order_no = get_next_order_no(sch_part_id, SchChapter, 'sch_part_id')
            
            # Create new schedule chapter
            sch_chapter = SchChapter(
                sch_part_id=sch_part_id,
                name=form.name.data,
                chapter_no=form.chapter_no.data,
                order_no=order_no,
                created_at=datetime.now(pytz.UTC),
                updated_at=datetime.now(pytz.UTC)
            )
            
            # Save the schedule chapter
            success, message = save_with_transaction(sch_chapter)
            if success:
                flash(f"Schedule chapter '{sch_chapter.name}' added successfully.", "success")
                
                # Handle different actions
                action = request.form.get('action', 'save')
                if action == 'save_add_another':
                    return redirect(url_for('schedule.add_sch_chapter', sch_part_id=sch_part_id))
                elif action == 'save_add_set':
                    return redirect(url_for('schedule.add_sch_set', sch_chapter_id=sch_chapter.id))
                else:
                    return redirect(url_for('statute.view_statute', statute_id=sch_part.statute_id))
            else:
                flash(message, "danger")
        
        return render_template(
            'schedule/add_chapter.html', 
            form=form, 
            sch_part=sch_part,
            statute=statute
        )
    except Exception as e:
        current_app.logger.error(f"Error adding schedule chapter: {str(e)}")
        flash("An error occurred while adding the schedule chapter.", "danger")
        return redirect(url_for('statute.list_statutes'))

@schedule_bp.route('/chapter/<int:sch_chapter_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_sch_chapter(sch_chapter_id):
    """Edit an existing schedule chapter"""
    try:
        # Get the schedule chapter
        sch_chapter = db.session.query(SchChapter).filter(SchChapter.id == sch_chapter_id).first()
        if not sch_chapter:
            flash("Schedule chapter not found.", "danger")
            return redirect(url_for('statute.list_statutes'))
        
        # Get the schedule part and statute for breadcrumb
        sch_part = db.session.query(SchPart).filter(SchPart.id == sch_chapter.sch_part_id).first()
        statute = db.session.query(Statute).filter(Statute.id == sch_part.statute_id).first()
        
        # Create form and populate with existing data
        form = SchChapterForm(obj=sch_chapter)
        
        if request.method == 'POST' and form.validate_on_submit():
            # Update schedule chapter
            sch_chapter.name = form.name.data
            sch_chapter.chapter_no = form.chapter_no.data
            sch_chapter.updated_at = datetime.now(pytz.UTC)
            
            # Save the changes
            success, message = save_with_transaction(sch_chapter)
            if success:
                flash(f"Schedule chapter '{sch_chapter.name}' updated successfully.", "success")
                return redirect(url_for('statute.view_statute', statute_id=sch_part.statute_id))
            else:
                flash(message, "danger")
        
        return render_template(
            'schedule/edit_chapter.html', 
            form=form, 
            sch_chapter=sch_chapter,
            sch_part=sch_part,
            statute=statute
        )
    except Exception as e:
        current_app.logger.error(f"Error editing schedule chapter: {str(e)}")
        flash("An error occurred while editing the schedule chapter.", "danger")
        return redirect(url_for('statute.list_statutes'))

@schedule_bp.route('/chapter/<int:sch_chapter_id>/delete', methods=['POST'])
@login_required
def delete_sch_chapter(sch_chapter_id):
    """Delete a schedule chapter and all its components"""
    try:
        # Get the schedule chapter
        sch_chapter = db.session.query(SchChapter).filter(SchChapter.id == sch_chapter_id).first()
        if not sch_chapter:
            flash("Schedule chapter not found.", "danger")
            return redirect(url_for('statute.list_statutes'))
        
        sch_part = db.session.query(SchPart).filter(SchPart.id == sch_chapter.sch_part_id).first()
        statute_id = sch_part.statute_id
        
        # Delete the schedule chapter (cascade will delete all children)
        db.session.delete(sch_chapter)
        db.session.commit()
        
        flash(f"Schedule chapter '{sch_chapter.name}' and all its components have been deleted.", "success")
        return redirect(url_for('statute.view_statute', statute_id=statute_id))
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Database error deleting schedule chapter: {str(e)}")
        flash("A database error occurred while deleting the schedule chapter.", "danger")
        return redirect(url_for('statute.list_statutes'))
    except Exception as e:
        current_app.logger.error(f"Error deleting schedule chapter: {str(e)}")
        flash("An error occurred while deleting the schedule chapter.", "danger")
        return redirect(url_for('statute.list_statutes'))

# Schedule Set routes
@schedule_bp.route('/chapter/<int:sch_chapter_id>/set/new', methods=['GET', 'POST'])
@login_required
def add_sch_set(sch_chapter_id):
    """Add a new schedule set to a chapter"""
    try:
        # Get the schedule chapter
        sch_chapter = db.session.query(SchChapter).filter(SchChapter.id == sch_chapter_id).first()
        if not sch_chapter:
            flash("Schedule chapter not found.", "danger")
            return redirect(url_for('statute.list_statutes'))
        
        # Get the schedule part and statute for breadcrumb
        sch_part = db.session.query(SchPart).filter(SchPart.id == sch_chapter.sch_part_id).first()
        statute = db.session.query(Statute).filter(Statute.id == sch_part.statute_id).first()
        
        # Create form
        form = SchSetForm()
        form.sch_chapter_id.data = sch_chapter_id
        
        if request.method == 'POST' and form.validate_on_submit():
            # Get next order number
            order_no = get_next_order_no(sch_chapter_id, SchSet, 'sch_chapter_id')
            
            # Create new schedule set
            sch_set = SchSet(
                sch_chapter_id=sch_chapter_id,
                name=form.name.data,
                set_no=form.set_no.data,
                order_no=order_no,
                created_at=datetime.now(pytz.UTC),
                updated_at=datetime.now(pytz.UTC)
            )
            
            # Save the schedule set
            success, message = save_with_transaction(sch_set)
            if success:
                flash(f"Schedule set '{sch_set.name}' added successfully.", "success")
                
                # Handle different actions
                action = request.form.get('action', 'save')
                if action == 'save_add_another':
                    return redirect(url_for('schedule.add_sch_set', sch_chapter_id=sch_chapter_id))
                elif action == 'save_add_section':
                    return redirect(url_for('schedule.add_sch_section', sch_set_id=sch_set.id))
                else:
                    return redirect(url_for('statute.view_statute', statute_id=sch_part.statute_id))
            else:
                flash(message, "danger")
        
        return render_template(
            'schedule/add_set.html', 
            form=form, 
            sch_chapter=sch_chapter,
            sch_part=sch_part,
            statute=statute
        )
    except Exception as e:
        current_app.logger.error(f"Error adding schedule set: {str(e)}")
        flash("An error occurred while adding the schedule set.", "danger")
        return redirect(url_for('statute.list_statutes'))

@schedule_bp.route('/set/<int:sch_set_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_sch_set(sch_set_id):
    """Edit an existing schedule set"""
    try:
        # Get the schedule set
        sch_set = db.session.query(SchSet).filter(SchSet.id == sch_set_id).first()
        if not sch_set:
            flash("Schedule set not found.", "danger")
            return redirect(url_for('statute.list_statutes'))
        
        # Get the schedule chapter, part and statute for breadcrumb
        sch_chapter = db.session.query(SchChapter).filter(SchChapter.id == sch_set.sch_chapter_id).first()
        sch_part = db.session.query(SchPart).filter(SchPart.id == sch_chapter.sch_part_id).first()
        statute = db.session.query(Statute).filter(Statute.id == sch_part.statute_id).first()
        
        # Create form and populate with existing data
        form = SchSetForm(obj=sch_set)
        
        if request.method == 'POST' and form.validate_on_submit():
            # Update schedule set
            sch_set.name = form.name.data
            sch_set.set_no = form.set_no.data
            sch_set.updated_at = datetime.now(pytz.UTC)
            
            # Save the changes
            success, message = save_with_transaction(sch_set)
            if success:
                flash(f"Schedule set '{sch_set.name}' updated successfully.", "success")
                return redirect(url_for('statute.view_statute', statute_id=sch_part.statute_id))
            else:
                flash(message, "danger")
        
        return render_template(
            'schedule/edit_set.html', 
            form=form, 
            sch_set=sch_set,
            sch_chapter=sch_chapter,
            sch_part=sch_part,
            statute=statute
        )
    except Exception as e:
        current_app.logger.error(f"Error editing schedule set: {str(e)}")
        flash("An error occurred while editing the schedule set.", "danger")
        return redirect(url_for('statute.list_statutes'))

@schedule_bp.route('/set/<int:sch_set_id>/delete', methods=['POST'])
@login_required
def delete_sch_set(sch_set_id):
    """Delete a schedule set and all its components"""
    try:
        # Get the schedule set
        sch_set = db.session.query(SchSet).filter(SchSet.id == sch_set_id).first()
        if not sch_set:
            flash("Schedule set not found.", "danger")
            return redirect(url_for('statute.list_statutes'))
        
        sch_chapter = db.session.query(SchChapter).filter(SchChapter.id == sch_set.sch_chapter_id).first()
        sch_part = db.session.query(SchPart).filter(SchPart.id == sch_chapter.sch_part_id).first()
        statute_id = sch_part.statute_id
        
        # Delete the schedule set (cascade will delete all children)
        db.session.delete(sch_set)
        db.session.commit()
        
        flash(f"Schedule set '{sch_set.name}' and all its components have been deleted.", "success")
        return redirect(url_for('statute.view_statute', statute_id=statute_id))
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Database error deleting schedule set: {str(e)}")
        flash("A database error occurred while deleting the schedule set.", "danger")
        return redirect(url_for('statute.list_statutes'))
    except Exception as e:
        current_app.logger.error(f"Error deleting schedule set: {str(e)}")
        flash("An error occurred while deleting the schedule set.", "danger")
        return redirect(url_for('statute.list_statutes'))

# Schedule Section routes
@schedule_bp.route('/set/<int:sch_set_id>/section/new', methods=['GET', 'POST'])
@login_required
def add_sch_section(sch_set_id):
    """Add a new schedule section to a set"""
    try:
        # Get the schedule set
        sch_set = db.session.query(SchSet).filter(SchSet.id == sch_set_id).first()
        if not sch_set:
            flash("Schedule set not found.", "danger")
            return redirect(url_for('statute.list_statutes'))
        
        # Get the schedule chapter, part and statute for breadcrumb
        sch_chapter = db.session.query(SchChapter).filter(SchChapter.id == sch_set.sch_chapter_id).first()
        sch_part = db.session.query(SchPart).filter(SchPart.id == sch_chapter.sch_part_id).first()
        statute = db.session.query(Statute).filter(Statute.id == sch_part.statute_id).first()
        
        # Create form
        form = SchSectionForm()
        form.sch_set_id.data = sch_set_id
        
        if request.method == 'POST' and form.validate_on_submit():
            # Get next order number
            order_no = get_next_order_no(sch_set_id, SchSection, 'sch_set_id')
            
            # Create new schedule section
            sch_section = SchSection(
                sch_set_id=sch_set_id,
                name=form.name.data,
                section_no=form.section_no.data,
                order_no=order_no,
                created_at=datetime.now(pytz.UTC),
                updated_at=datetime.now(pytz.UTC)
            )
            
            # Save the schedule section
            success, message = save_with_transaction(sch_section)
            if success:
                flash(f"Schedule section '{sch_section.name}' added successfully.", "success")
                
                # Handle different actions
                action = request.form.get('action', 'save')
                if action == 'save_add_another':
                    return redirect(url_for('schedule.add_sch_section', sch_set_id=sch_set_id))
                elif action == 'save_add_subsection':
                    return redirect(url_for('schedule.add_sch_subsection', sch_section_id=sch_section.id))
                else:
                    return redirect(url_for('statute.view_statute', statute_id=sch_part.statute_id))
            else:
                flash(message, "danger")
        
        
        return render_template(
            'schedule/add_section.html', 
            form=form, 
            sch_set=sch_set,
            sch_chapter=sch_chapter,
            sch_part=sch_part,
            statute=statute
        )
    except Exception as e:
        current_app.logger.error(f"Error adding schedule section: {str(e)}")
        flash("An error occurred while adding the schedule section.", "danger")
        return redirect(url_for('statute.list_statutes'))

@schedule_bp.route('/section/<int:sch_section_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_sch_section(sch_section_id):
    """Edit an existing schedule section"""
    try:
        # Get the schedule section
        sch_section = db.session.query(SchSection).filter(SchSection.id == sch_section_id).first()
        if not sch_section:
            flash("Schedule section not found.", "danger")
            return redirect(url_for('statute.list_statutes'))
        
        # Get the schedule set, chapter, part and statute for breadcrumb
        sch_set = db.session.query(SchSet).filter(SchSet.id == sch_section.sch_set_id).first()
        sch_chapter = db.session.query(SchChapter).filter(SchChapter.id == sch_set.sch_chapter_id).first()
        sch_part = db.session.query(SchPart).filter(SchPart.id == sch_chapter.sch_part_id).first()
        statute = db.session.query(Statute).filter(Statute.id == sch_part.statute_id).first()
        
        # Create form and populate with existing data
        form = SchSectionForm(obj=sch_section)
        
        if request.method == 'POST' and form.validate_on_submit():
            # Update schedule section
            sch_section.name = form.name.data
            sch_section.section_no = form.section_no.data
            sch_section.updated_at = datetime.now(pytz.UTC)
            
            # Save the changes
            success, message = save_with_transaction(sch_section)
            if success:
                flash(f"Schedule section '{sch_section.name}' updated successfully.", "success")
                return redirect(url_for('statute.view_statute', statute_id=sch_part.statute_id))
            else:
                flash(message, "danger")
        
        return render_template(
            'schedule/edit_section.html', 
            form=form, 
            sch_section=sch_section,
            sch_set=sch_set,
            sch_chapter=sch_chapter,
            sch_part=sch_part,
            statute=statute
        )
    except Exception as e:
        current_app.logger.error(f"Error editing schedule section: {str(e)}")
        flash("An error occurred while editing the schedule section.", "danger")
        return redirect(url_for('statute.list_statutes'))

@schedule_bp.route('/section/<int:sch_section_id>/delete', methods=['POST'])
@login_required
def delete_sch_section(sch_section_id):
    """Delete a schedule section and all its subsections"""
    try:
        # Get the schedule section
        sch_section = db.session.query(SchSection).filter(SchSection.id == sch_section_id).first()
        if not sch_section:
            flash("Schedule section not found.", "danger")
            return redirect(url_for('statute.list_statutes'))
        
        sch_set = db.session.query(SchSet).filter(SchSet.id == sch_section.sch_set_id).first()
        sch_chapter = db.session.query(SchChapter).filter(SchChapter.id == sch_set.sch_chapter_id).first()
        sch_part = db.session.query(SchPart).filter(SchPart.id == sch_chapter.sch_part_id).first()
        statute_id = sch_part.statute_id
        
        # Delete the schedule section (cascade will delete all children)
        db.session.delete(sch_section)
        db.session.commit()
        
        flash(f"Schedule section '{sch_section.name}' and all its subsections have been deleted.", "success")
        return redirect(url_for('statute.view_statute', statute_id=statute_id))
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Database error deleting schedule section: {str(e)}")
        flash("A database error occurred while deleting the schedule section.", "danger")
        return redirect(url_for('statute.list_statutes'))
    except Exception as e:
        current_app.logger.error(f"Error deleting schedule section: {str(e)}")
        flash("An error occurred while deleting the schedule section.", "danger")
        return redirect(url_for('statute.list_statutes'))

# Schedule Subsection routes
@schedule_bp.route('/section/<int:sch_section_id>/subsection/new', methods=['GET', 'POST'])
@login_required
def add_sch_subsection(sch_section_id):
    """Add a new schedule subsection to a section"""
    try:
        # Get the schedule section
        sch_section = db.session.query(SchSection).filter(SchSection.id == sch_section_id).first()
        if not sch_section:
            flash("Schedule section not found.", "danger")
            return redirect(url_for('statute.list_statutes'))
        
        # Get the schedule set, chapter, part and statute for breadcrumb
        sch_set = db.session.query(SchSet).filter(SchSet.id == sch_section.sch_set_id).first()
        sch_chapter = db.session.query(SchChapter).filter(SchChapter.id == sch_set.sch_chapter_id).first()
        sch_part = db.session.query(SchPart).filter(SchPart.id == sch_chapter.sch_part_id).first()
        statute = db.session.query(Statute).filter(Statute.id == sch_part.statute_id).first()
        
        # Create form
        form = SchSubsectionForm()
        form.sch_section_id.data = sch_section_id
        
        if request.method == 'POST' and form.validate_on_submit():
            # Get next order number
            order_no = get_next_order_no(sch_section_id, SchSubsection, 'sch_section_id')
            
            # Create new schedule subsection
            sch_subsection = SchSubsection(
                sch_section_id=sch_section_id,
                name=form.name.data,
                subsection_no=form.subsection_no.data,
                content=form.content.data,
                order_no=order_no,
                created_at=datetime.now(pytz.UTC),
                updated_at=datetime.now(pytz.UTC)
            )
            
            # Save the schedule subsection
            success, message = save_with_transaction(sch_subsection)
            if success:
                flash(f"Schedule subsection '{sch_subsection.name}' added successfully.", "success")
                
                # Handle different actions
                action = request.form.get('action', 'save')
                if action == 'save_add_another':
                    return redirect(url_for('schedule.add_sch_subsection', sch_section_id=sch_section_id))
                else:
                    return redirect(url_for('statute.view_statute', statute_id=sch_part.statute_id))
            else:
                flash(message, "danger")
        
        return render_template(
            'schedule/add_subsection.html', 
            form=form, 
            sch_section=sch_section,
            sch_set=sch_set,
            sch_chapter=sch_chapter,
            sch_part=sch_part,
            statute=statute
        )
    except Exception as e:
        current_app.logger.error(f"Error adding schedule subsection: {str(e)}")
        flash("An error occurred while adding the schedule subsection.", "danger")
        return redirect(url_for('statute.list_statutes'))

@schedule_bp.route('/subsection/<int:sch_subsection_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_sch_subsection(sch_subsection_id):
    """Edit an existing schedule subsection"""
    try:
        # Get the schedule subsection
        sch_subsection = db.session.query(SchSubsection).filter(SchSubsection.id == sch_subsection_id).first()
        if not sch_subsection:
            flash("Schedule subsection not found.", "danger")
            return redirect(url_for('statute.list_statutes'))
        
        # Get the schedule section, set, chapter, schedule part and statute for breadcrumb
        sch_section = db.session.query(SchSection).filter(SchSection.id == sch_subsection.sch_section_id).first()
        sch_set = db.session.query(SchSet).filter(SchSet.id == sch_section.sch_set_id).first()
        sch_chapter = db.session.query(SchChapter).filter(SchChapter.id == sch_set.sch_chapter_id).first()
        schedule_part = db.session.query(SchPart).filter(SchPart.id == sch_chapter.sch_part_id).first()
        statute = db.session.query(Statute).filter(Statute.id == schedule_part.statute_id).first()
        
        # Create form and populate with existing data        
        form = SchSubsectionForm(obj=sch_subsection)
        
        if request.method == 'POST' and form.validate_on_submit():
            # Update schedule subsection
            sch_subsection.name = form.name.data
            sch_subsection.subsection_no = form.subsection_no.data
            sch_subsection.content = form.content.data
            sch_subsection.updated_at = datetime.now(pytz.UTC)
            
            # Save the changes
            success, message = save_with_transaction(sch_subsection)
            if success:
                flash(f"Schedule subsection '{sch_subsection.name}' updated successfully.", "success")
                return redirect(url_for('statute.view_statute', statute_id=schedule_part.statute_id))
            else:
                flash(message, "danger")
        
        return render_template(
            'schedule/edit_subsection.html', 
            form=form, 
            sch_subsection=sch_subsection,
            sch_section=sch_section,
            sch_set=sch_set,
            sch_chapter=sch_chapter,
            sch_part=schedule_part,
            statute=statute
        )
    except Exception as e:
        current_app.logger.error(f"Error editing schedule subsection: {str(e)}")
        flash("An error occurred while editing the schedule subsection.", "danger")
        return redirect(url_for('statute.list_statutes'))

@schedule_bp.route('/subsection/<int:sch_subsection_id>/delete', methods=['POST'])
@login_required
def delete_sch_subsection(sch_subsection_id):
    """Delete a schedule subsection"""
    try:
        # Get the schedule subsection
        sch_subsection = db.session.query(SchSubsection).filter(SchSubsection.id == sch_subsection_id).first()
        if not sch_subsection:
            flash("Schedule subsection not found.", "danger")
            return redirect(url_for('statute.list_statutes'))
        
        sch_section = db.session.query(SchSection).filter(SchSection.id == sch_subsection.sch_section_id).first()
        sch_set = db.session.query(SchSet).filter(SchSet.id == sch_section.sch_set_id).first()
        sch_chapter = db.session.query(SchChapter).filter(SchChapter.id == sch_set.sch_chapter_id).first()
        schedule_part = db.session.query(SchPart).filter(SchPart.id == sch_chapter.sch_part_id).first()
        statute_id = schedule_part.statute_id
        
        # Delete the schedule subsection
        db.session.delete(sch_subsection)
        db.session.commit()
        
        flash(f"Schedule subsection '{sch_subsection.name}' has been deleted.", "success")
        return redirect(url_for('statute.view_statute', statute_id=statute_id))
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Database error deleting schedule subsection: {str(e)}")
        flash("A database error occurred while deleting the schedule subsection.", "danger")
        return redirect(url_for('statute.list_statutes'))
    except Exception as e:
        current_app.logger.error(f"Error deleting schedule subsection: {str(e)}")
        flash("An error occurred while deleting the schedule subsection.", "danger")
        return redirect(url_for('statute.list_statutes'))