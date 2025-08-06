from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from sqlalchemy.exc import SQLAlchemyError
from models import db, Statute, Part, Chapter, Set, Section, Subsection
from forms import PartForm, ChapterForm, SetForm, SectionForm, SubsectionForm
from database import save_with_transaction, get_next_order_no
from datetime import datetime
import pytz
from flask_login import login_required
# Create blueprint
hierarchy_bp = Blueprint('hierarchy', __name__)

# Part routes
@hierarchy_bp.route('/statute/<int:statute_id>/part/new', methods=['GET', 'POST'])
@login_required
def add_part(statute_id):
    """Add a new part to a statute"""
    try:
        # Get the statute
        statute = db.session.query(Statute).filter(Statute.id == statute_id).first()
        if not statute:
            flash("Statute not found.", "danger")
            return redirect(url_for('statute.list_statutes'))
        
        # Create form
        form = PartForm()
        form.statute_id.data = statute_id
        
        if request.method == 'POST' and form.validate_on_submit():
            # Get next order number
            order_no = get_next_order_no(statute_id, Part, 'statute_id')
            
            # Create new part
            part = Part(
                statute_id=statute_id,
                name=form.name.data,
                part_no=form.part_no.data,
                order_no=order_no,
                created_at=datetime.now(pytz.UTC),
                updated_at=datetime.now(pytz.UTC)
            )
            
            # Save the part
            success, message = save_with_transaction(part)
            if success:
                flash(f"Part '{part.name}' added successfully.", "success")
                
                # Handle different actions
                action = request.form.get('action', 'save')
                if action == 'save_add_another':
                    return redirect(url_for('hierarchy.add_part', statute_id=statute_id))
                elif action == 'save_add_chapter':
                    return redirect(url_for('hierarchy.add_chapter', part_id=part.id))
                else:
                    return redirect(url_for('statute.view_statute', statute_id=statute_id))
            else:
                flash(message, "danger")
        
        
        return render_template(
            'hierarchy/add_part.html', 
            form=form, 
            statute=statute
        )
    except Exception as e:
        current_app.logger.error(f"Error adding part: {str(e)}")
        flash("An error occurred while adding the part.", "danger")
        return redirect(url_for('statute.view_statute', statute_id=statute_id))

@hierarchy_bp.route('/part/<int:part_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_part(part_id):
    """Edit an existing part"""
    try:
        # Get the part
        part = db.session.query(Part).filter(Part.id == part_id).first()
        if not part:
            flash("Part not found.", "danger")
            return redirect(url_for('statute.list_statutes'))
        
        # Get the statute for breadcrumb
        statute = db.session.query(Statute).filter(Statute.id == part.statute_id).first()
        
        # Create form and populate with existing data
        form = PartForm(obj=part)
        
        if request.method == 'POST' and form.validate_on_submit():
            # Update part
            part.name = form.name.data
            part.part_no = form.part_no.data
            part.updated_at = datetime.now(pytz.UTC)
            
            # Save the changes
            success, message = save_with_transaction(part)
            if success:
                flash(f"Part '{part.name}' updated successfully.", "success")
                return redirect(url_for('statute.view_statute', statute_id=part.statute_id))
            else:
                flash(message, "danger")
        
        return render_template(
            'hierarchy/edit_part.html', 
            form=form, 
            part=part,
            statute=statute
        )
    except Exception as e:
        current_app.logger.error(f"Error editing part: {str(e)}")
        flash("An error occurred while editing the part.", "danger")
        return redirect(url_for('statute.list_statutes'))

@hierarchy_bp.route('/part/<int:part_id>/delete', methods=['POST'])
@login_required
def delete_part(part_id):
    """Delete a part and all its components"""
    try:
        # Get the part
        part = db.session.query(Part).filter(Part.id == part_id).first()
        if not part:
            flash("Part not found.", "danger")
            return redirect(url_for('statute.list_statutes'))
        
        statute_id = part.statute_id
        
        # Delete the part (cascade will delete all children)
        db.session.delete(part)
        db.session.commit()
        
        flash(f"Part '{part.name}' and all its components have been deleted.", "success")
        return redirect(url_for('statute.view_statute', statute_id=statute_id))
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Database error deleting part: {str(e)}")
        flash("A database error occurred while deleting the part.", "danger")
        return redirect(url_for('statute.list_statutes'))
    except Exception as e:
        current_app.logger.error(f"Error deleting part: {str(e)}")
        flash("An error occurred while deleting the part.", "danger")
        return redirect(url_for('statute.list_statutes'))

@hierarchy_bp.route('/part/<int:part_id>/chapter/new', methods=['GET', 'POST'])
@login_required
def add_chapter(part_id):
    """Add a new chapter to a part"""
    try:
        # Get the part
        part = db.session.query(Part).filter(Part.id == part_id).first()
        if not part:
            flash("Part not found.", "danger")
            return redirect(url_for('statute.list_statutes'))
        
        # Get the statute for breadcrumb
        statute = db.session.query(Statute).filter(Statute.id == part.statute_id).first()
        
        # Create form
        form = ChapterForm()
        form.part_id.data = part_id
        
        if request.method == 'POST' and form.validate_on_submit():
            # Get next order number
            order_no = get_next_order_no(part_id, Chapter, 'part_id')
            
            # Create new chapter
            chapter = Chapter(
                part_id=part_id,
                name=form.name.data,
                chapter_no=form.chapter_no.data,
                order_no=order_no,
                created_at=datetime.now(pytz.UTC),
                updated_at=datetime.now(pytz.UTC)
            )
            
            # Save the chapter
            success, message = save_with_transaction(chapter)
            if success:
                flash(f"Chapter '{chapter.name}' added successfully.", "success")
                
                # Handle different actions
                action = request.form.get('action', 'save')
                if action == 'save_add_another':
                    return redirect(url_for('hierarchy.add_chapter', part_id=part_id))
                elif action == 'save_add_set':
                    return redirect(url_for('hierarchy.add_set', chapter_id=chapter.id))
                else:
                    return redirect(url_for('statute.view_statute', statute_id=part.statute_id))
            else:
                flash(message, "danger")
        
        
        return render_template(
            'hierarchy/add_chapter.html', 
            form=form, 
            part=part,
            statute=statute
        )
    except Exception as e:
        current_app.logger.error(f"Error adding chapter: {str(e)}")
        flash("An error occurred while adding the chapter.", "danger")
        return redirect(url_for('statute.list_statutes'))

@hierarchy_bp.route('/chapter/<int:chapter_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_chapter(chapter_id):
    """Edit an existing chapter"""
    try:
        # Get the chapter
        chapter = db.session.query(Chapter).filter(Chapter.id == chapter_id).first()
        if not chapter:
            flash("Chapter not found.", "danger")
            return redirect(url_for('statute.list_statutes'))
        
        # Get the part and statute for breadcrumb
        part = db.session.query(Part).filter(Part.id == chapter.part_id).first()
        statute = db.session.query(Statute).filter(Statute.id == part.statute_id).first()
        
        # Create form and populate with existing data
        form = ChapterForm(obj=chapter)
        
        if request.method == 'POST' and form.validate_on_submit():
            # Update chapter
            chapter.name = form.name.data
            chapter.chapter_no = form.chapter_no.data
            chapter.updated_at = datetime.now(pytz.UTC)
            
            # Save the changes
            success, message = save_with_transaction(chapter)
            if success:
                flash(f"Chapter '{chapter.name}' updated successfully.", "success")
                return redirect(url_for('statute.view_statute', statute_id=part.statute_id))
            else:
                flash(message, "danger")
        
        return render_template(
            'hierarchy/edit_chapter.html', 
            form=form, 
            chapter=chapter,
            part=part,
            statute=statute
        )
    except Exception as e:
        current_app.logger.error(f"Error editing chapter: {str(e)}")
        flash("An error occurred while editing the chapter.", "danger")
        return redirect(url_for('statute.list_statutes'))

@hierarchy_bp.route('/chapter/<int:chapter_id>/delete', methods=['POST'])
@login_required
def delete_chapter(chapter_id):
    """Delete a chapter and all its components"""
    try:
        # Get the chapter
        chapter = db.session.query(Chapter).filter(Chapter.id == chapter_id).first()
        if not chapter:
            flash("Chapter not found.", "danger")
            return redirect(url_for('statute.list_statutes'))
        
        part = db.session.query(Part).filter(Part.id == chapter.part_id).first()
        statute_id = part.statute_id
        
        # Delete the chapter (cascade will delete all children)
        db.session.delete(chapter)
        db.session.commit()
        
        flash(f"Chapter '{chapter.name}' and all its components have been deleted.", "success")
        return redirect(url_for('statute.view_statute', statute_id=statute_id))
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Database error deleting chapter: {str(e)}")
        flash("A database error occurred while deleting the chapter.", "danger")
        return redirect(url_for('statute.list_statutes'))
    except Exception as e:
        current_app.logger.error(f"Error deleting chapter: {str(e)}")
        flash("An error occurred while deleting the chapter.", "danger")
        return redirect(url_for('statute.list_statutes'))

@hierarchy_bp.route('/chapter/<int:chapter_id>/set/new', methods=['GET', 'POST'])
@login_required
def add_set(chapter_id):
    """Add a new set to a chapter"""
    try:
        # Get the chapter
        chapter = db.session.query(Chapter).filter(Chapter.id == chapter_id).first()
        if not chapter:
            flash("Chapter not found.", "danger")
            return redirect(url_for('statute.list_statutes'))
        
        # Get the part and statute for breadcrumb
        part = db.session.query(Part).filter(Part.id == chapter.part_id).first()
        statute = db.session.query(Statute).filter(Statute.id == part.statute_id).first()
        
        # Create form
        form = SetForm()
        form.chapter_id.data = chapter_id
        
        if request.method == 'POST' and form.validate_on_submit():
            # Get next order number
            order_no = get_next_order_no(chapter_id, Set, 'chapter_id')
            
            # Create new set
            set_item = Set(
                chapter_id=chapter_id,
                name=form.name.data,
                set_no=form.set_no.data,
                order_no=order_no,
                created_at=datetime.now(pytz.UTC),
                updated_at=datetime.now(pytz.UTC)
            )
            
            # Save the set
            success, message = save_with_transaction(set_item)
            if success:
                flash(f"Set '{set_item.name}' added successfully.", "success")
                
                # Handle different actions
                action = request.form.get('action', 'save')
                if action == 'save_add_another':
                    return redirect(url_for('hierarchy.add_set', chapter_id=chapter_id))
                elif action == 'save_add_section':
                    return redirect(url_for('hierarchy.add_section', set_id=set_item.id))
                else:
                    return redirect(url_for('statute.view_statute', statute_id=part.statute_id))
            else:
                flash(message, "danger")
        
        
        return render_template(
            'hierarchy/add_set.html', 
            form=form, 
            chapter=chapter,
            part=part,
            statute=statute
        )
    except Exception as e:
        current_app.logger.error(f"Error adding set: {str(e)}")
        flash("An error occurred while adding the set.", "danger")
        return redirect(url_for('statute.list_statutes'))

@hierarchy_bp.route('/set/<int:set_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_set(set_id):
    """Edit an existing set"""
    try:
        # Get the set
        set_item = db.session.query(Set).filter(Set.id == set_id).first()
        if not set_item:
            flash("Set not found.", "danger")
            return redirect(url_for('statute.list_statutes'))
        
        # Get the chapter, part and statute for breadcrumb
        chapter = db.session.query(Chapter).filter(Chapter.id == set_item.chapter_id).first()
        part = db.session.query(Part).filter(Part.id == chapter.part_id).first()
        statute = db.session.query(Statute).filter(Statute.id == part.statute_id).first()
        
        # Create form and populate with existing data
        form = SetForm(obj=set_item)
        
        if request.method == 'POST' and form.validate_on_submit():
            # Update set
            set_item.name = form.name.data
            set_item.set_no = form.set_no.data
            set_item.updated_at = datetime.now(pytz.UTC)
            
            # Save the changes
            success, message = save_with_transaction(set_item)
            if success:
                flash(f"Set '{set_item.name}' updated successfully.", "success")
                return redirect(url_for('statute.view_statute', statute_id=part.statute_id))
            else:
                flash(message, "danger")
        
        return render_template(
            'hierarchy/edit_set.html', 
            form=form, 
            set=set_item,
            chapter=chapter,
            part=part,
            statute=statute
        )
    except Exception as e:
        current_app.logger.error(f"Error editing set: {str(e)}")
        flash("An error occurred while editing the set.", "danger")
        return redirect(url_for('statute.list_statutes'))

@hierarchy_bp.route('/set/<int:set_id>/delete', methods=['POST'])
@login_required
def delete_set(set_id):
    """Delete a set and all its components"""
    try:
        # Get the set
        set_item = db.session.query(Set).filter(Set.id == set_id).first()
        if not set_item:
            flash("Set not found.", "danger")
            return redirect(url_for('statute.list_statutes'))
        
        chapter = db.session.query(Chapter).filter(Chapter.id == set_item.chapter_id).first()
        part = db.session.query(Part).filter(Part.id == chapter.part_id).first()
        statute_id = part.statute_id
        
        # Delete the set (cascade will delete all children)
        db.session.delete(set_item)
        db.session.commit()
        
        flash(f"Set '{set_item.name}' and all its components have been deleted.", "success")
        return redirect(url_for('statute.view_statute', statute_id=statute_id))
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Database error deleting set: {str(e)}")
        flash("A database error occurred while deleting the set.", "danger")
        return redirect(url_for('statute.list_statutes'))
    except Exception as e:
        current_app.logger.error(f"Error deleting set: {str(e)}")
        flash("An error occurred while deleting the set.", "danger")
        return redirect(url_for('statute.list_statutes'))

@hierarchy_bp.route('/set/<int:set_id>/section/new', methods=['GET', 'POST'])
@login_required
def add_section(set_id):
    """Add a new section to a set"""
    try:
        # Get the set
        set_item = db.session.query(Set).filter(Set.id == set_id).first()
        if not set_item:
            flash("Set not found.", "danger")
            return redirect(url_for('statute.list_statutes'))
        
        # Get the chapter, part and statute for breadcrumb
        chapter = db.session.query(Chapter).filter(Chapter.id == set_item.chapter_id).first()
        part = db.session.query(Part).filter(Part.id == chapter.part_id).first()
        statute = db.session.query(Statute).filter(Statute.id == part.statute_id).first()
        
        # Create form
        form = SectionForm()
        form.set_id.data = set_id
        
        if request.method == 'POST' and form.validate_on_submit():
            # Get next order number
            order_no = get_next_order_no(set_id, Section, 'set_id')
            
            # Create new section
            section = Section(
                set_id=set_id,
                name=form.name.data,
                section_no=form.section_no.data,
                order_no=order_no,
                created_at=datetime.now(pytz.UTC),
                updated_at=datetime.now(pytz.UTC)
            )
            
            # Save the section
            success, message = save_with_transaction(section)
            if success:
                flash(f"Section '{section.name}' added successfully.", "success")
                
                # Handle different actions
                action = request.form.get('action', 'save')
                print('=====================================', request.form)
                print(action)
                if action == 'save_add_another':
                    return redirect(url_for('hierarchy.add_section', set_id=set_id))
                elif action == 'save_add_subsection':
                    return redirect(url_for('hierarchy.add_subsection', section_id=section.id))
                else:
                    return redirect(url_for('statute.view_statute', statute_id=part.statute_id))
            else:
                flash(message, "danger")
        
        
        return render_template(
            'hierarchy/add_section.html', 
            form=form, 
            set=set_item,
            chapter=chapter,
            part=part,
            statute=statute
        )
    except Exception as e:
        current_app.logger.error(f"Error adding section: {str(e)}")
        flash("An error occurred while adding the section.", "danger")
        return redirect(url_for('statute.list_statutes'))

@hierarchy_bp.route('/section/<int:section_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_section(section_id):
    """Edit an existing section"""
    try:
        # Get the section
        section = db.session.query(Section).filter(Section.id == section_id).first()
        if not section:
            flash("Section not found.", "danger")
            return redirect(url_for('statute.list_statutes'))
        
        # Get the set, chapter, part and statute for breadcrumb
        set_item = db.session.query(Set).filter(Set.id == section.set_id).first()
        chapter = db.session.query(Chapter).filter(Chapter.id == set_item.chapter_id).first()
        part = db.session.query(Part).filter(Part.id == chapter.part_id).first()
        statute = db.session.query(Statute).filter(Statute.id == part.statute_id).first()
        
        # Create form and populate with existing data
        form = SectionForm(obj=section)
        
        if request.method == 'POST' and form.validate_on_submit():
            # Update section
            section.name = form.name.data
            section.section_no = form.section_no.data
            section.updated_at = datetime.now(pytz.UTC)
            
            # Save the changes
            success, message = save_with_transaction(section)
            if success:
                flash(f"Section '{section.name}' updated successfully.", "success")
                return redirect(url_for('statute.view_statute', statute_id=part.statute_id))
            else:
                flash(message, "danger")
        
        return render_template(
            'hierarchy/edit_section.html', 
            form=form, 
            section=section,
            set=set_item,
            chapter=chapter,
            part=part,
            statute=statute
        )
    except Exception as e:
        current_app.logger.error(f"Error editing section: {str(e)}")
        flash("An error occurred while editing the section.", "danger")
        return redirect(url_for('statute.list_statutes'))

@hierarchy_bp.route('/section/<int:section_id>/delete', methods=['POST'])
@login_required
def delete_section(section_id):
    """Delete a section and all its subsections"""
    try:
        # Get the section
        section = db.session.query(Section).filter(Section.id == section_id).first()
        if not section:
            flash("Section not found.", "danger")
            return redirect(url_for('statute.list_statutes'))
        
        set_item = db.session.query(Set).filter(Set.id == section.set_id).first()
        chapter = db.session.query(Chapter).filter(Chapter.id == set_item.chapter_id).first()
        part = db.session.query(Part).filter(Part.id == chapter.part_id).first()
        statute_id = part.statute_id
        
        # Delete the section (cascade will delete all children)
        db.session.delete(section)
        db.session.commit()
        
        flash(f"Section '{section.name}' and all its subsections have been deleted.", "success")
        return redirect(url_for('statute.view_statute', statute_id=statute_id))
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Database error deleting section: {str(e)}")
        flash("A database error occurred while deleting the section.", "danger")
        return redirect(url_for('statute.list_statutes'))
    except Exception as e:
        current_app.logger.error(f"Error deleting section: {str(e)}")
        flash("An error occurred while deleting the section.", "danger")
        return redirect(url_for('statute.list_statutes'))


@hierarchy_bp.route('/section/<int:section_id>/subsection/new', methods=['GET', 'POST'])
@login_required
def add_subsection(section_id):
    """Add a new subsection to a section"""
    try:
        # Get the section
        section = db.session.query(Section).filter(Section.id == section_id).first()
        if not section:
            flash("Section not found.", "danger")
            return redirect(url_for('statute.list_statutes'))
        
        # Get the set, chapter, part and statute for breadcrumb
        set_item = db.session.query(Set).filter(Set.id == section.set_id).first()
        chapter = db.session.query(Chapter).filter(Chapter.id == set_item.chapter_id).first()
        part = db.session.query(Part).filter(Part.id == chapter.part_id).first()
        statute = db.session.query(Statute).filter(Statute.id == part.statute_id).first()
        
        # Create form
        form = SubsectionForm()
        form.section_id.data = section_id
        
        if request.method == 'POST' and form.validate_on_submit():
            # Get next order number
            order_no = get_next_order_no(section_id, Subsection, 'section_id')
            
            # Create new subsection
            subsection = Subsection(
                section_id=section_id,
                name=form.name.data,
                subsection_no=form.subsection_no.data,
                content=form.content.data,
                order_no=order_no,
                created_at=datetime.now(pytz.UTC),
                updated_at=datetime.now(pytz.UTC)
            )
            
            # Save the subsection
            success, message = save_with_transaction(subsection)
            if success:
                flash(f"Subsection '{subsection.name}' added successfully.", "success")
                
                # Handle different actions
                action = request.form.get('action', 'save')
                if action == 'save_add_another':
                    return redirect(url_for('hierarchy.add_subsection', section_id=section_id))
                if action == 'save_add_section':
                    return redirect(url_for('hierarchy.add_section', set_id=section.set_id))
                else:
                    return redirect(url_for('statute.view_statute', statute_id=part.statute_id))
            else:
                flash(message, "danger")
    
        
        return render_template(
            'hierarchy/add_subsection.html', 
            form=form, 
            section=section,
            set=set_item,
            chapter=chapter,
            part=part,
            statute=statute
        )
    except Exception as e:
        current_app.logger.error(f"Error adding subsection: {str(e)}")
        flash("An error occurred while adding the subsection.", "danger")
        return redirect(url_for('statute.list_statutes'))


@hierarchy_bp.route('/subsection/<int:subsection_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_subsection(subsection_id):
    """Edit an existing subsection"""
    try:
        # Get the subsection
        subsection = db.session.query(Subsection).filter(Subsection.id == subsection_id).first()
        if not subsection:
            flash("Subsection not found.", "danger")
            return redirect(url_for('statute.list_statutes'))
        
        # Get the section, set, chapter, part and statute for breadcrumb
        section = db.session.query(Section).filter(Section.id == subsection.section_id).first()
        set_item = db.session.query(Set).filter(Set.id == section.set_id).first()
        chapter = db.session.query(Chapter).filter(Chapter.id == set_item.chapter_id).first()
        part = db.session.query(Part).filter(Part.id == chapter.part_id).first()
        statute = db.session.query(Statute).filter(Statute.id == part.statute_id).first()
        
        # Create form and populate with existing data
        form = SubsectionForm(obj=subsection)
        
        if request.method == 'POST' and form.validate_on_submit():
            # Update subsection
            subsection.name = form.name.data
            subsection.subsection_no = form.subsection_no.data
            subsection.content = form.content.data
            subsection.updated_at = datetime.now(pytz.UTC)
            
            # Save the changes
            success, message = save_with_transaction(subsection)
            if success:
                flash(f"Subsection '{subsection.name}' updated successfully.", "success")
                return redirect(url_for('statute.view_statute', statute_id=part.statute_id))
            else:
                flash(message, "danger")
        
        return render_template(
            'hierarchy/edit_subsection.html', 
            form=form, 
            subsection=subsection,
            section=section,
            set=set_item,
            chapter=chapter,
            part=part,
            statute=statute
        )
    except Exception as e:
        current_app.logger.error(f"Error editing subsection: {str(e)}")
        flash("An error occurred while editing the subsection.", "danger")
        return redirect(url_for('statute.list_statutes'))

@hierarchy_bp.route('/subsection/<int:subsection_id>/delete', methods=['POST'])
@login_required
def delete_subsection(subsection_id):
    """Delete a subsection"""
    try:
        # Get the subsection
        subsection = db.session.query(Subsection).filter(Subsection.id == subsection_id).first()
        if not subsection:
            flash("Subsection not found.", "danger")
            return redirect(url_for('statute.list_statutes'))
        
        section = db.session.query(Section).filter(Section.id == subsection.section_id).first()
        set_item = db.session.query(Set).filter(Set.id == section.set_id).first()
        chapter = db.session.query(Chapter).filter(Chapter.id == set_item.chapter_id).first()
        part = db.session.query(Part).filter(Part.id == chapter.part_id).first()
        statute_id = part.statute_id
        
        # Delete the subsection
        db.session.delete(subsection)
        db.session.commit()
        
        flash(f"Subsection '{subsection.name}' has been deleted.", "success")
        return redirect(url_for('statute.view_statute', statute_id=statute_id))
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Database error deleting subsection: {str(e)}")
        flash("An error occurred while deleting the subsection.", "danger")
        return redirect(url_for('statute.list_statutes'))
    except Exception as e:
        current_app.logger.error(f"Error deleting subsection: {str(e)}")
        flash("An error occurred while deleting the subsection.", "danger")
        return redirect(url_for('statute.list_statutes'))


@hierarchy_bp.route('/hierarchy/component', methods=['POST'])
@login_required
def component_api():
    """Generic API endpoint to manage hierarchy components."""
    try:
        data = request.get_json() or {}
        action = data.get('action')
        comp_type = data.get('type')

        component_map = {
            'part': (Part, 'statute_id'),
            'chapter': (Chapter, 'part_id'),
            'set': (Set, 'chapter_id'),
            'section': (Section, 'set_id'),
            'subsection': (Subsection, 'section_id')
        }

        if comp_type not in component_map:
            return jsonify({'success': False, 'message': 'Invalid component type'}), 400

        model, parent_field = component_map[comp_type]

        if action == 'add':
            parent_id = data.get('parent_id')
            fields = {
                'name': data.get('name'),
                'order_no': get_next_order_no(parent_id, model, parent_field),
                'created_at': datetime.now(pytz.UTC),
                'updated_at': datetime.now(pytz.UTC)
            }
            number_field = f"{comp_type}_no"
            if number_field in model.__table__.columns and data.get('number') is not None:
                fields[number_field] = data.get('number')
            if comp_type == 'subsection':
                fields['content'] = data.get('content', '')

            fields[parent_field] = parent_id
            obj = model(**fields)
            success, message = save_with_transaction(obj)
            if success:
                return jsonify({'success': True, 'component': obj.to_dict()})
            return jsonify({'success': False, 'message': message}), 400

        elif action == 'edit':
            comp_id = data.get('id')
            obj = db.session.query(model).filter(model.id == comp_id).first()
            if not obj:
                return jsonify({'success': False, 'message': 'Component not found'}), 404
            if data.get('name') is not None:
                obj.name = data.get('name')
            number_field = f"{comp_type}_no"
            if number_field in model.__table__.columns and data.get('number') is not None:
                setattr(obj, number_field, data.get('number'))
            if comp_type == 'subsection' and data.get('content') is not None:
                obj.content = data.get('content')
            obj.updated_at = datetime.now(pytz.UTC)
            success, message = save_with_transaction(obj)
            if success:
                return jsonify({'success': True, 'component': obj.to_dict()})
            return jsonify({'success': False, 'message': message}), 400

        elif action == 'delete':
            comp_id = data.get('id')
            obj = db.session.query(model).filter(model.id == comp_id).first()
            if not obj:
                return jsonify({'success': False, 'message': 'Component not found'}), 404
            db.session.delete(obj)
            db.session.commit()
            return jsonify({'success': True})

        elif action == 'reorder':
            parent_id = data.get('parent_id')
            order = data.get('order', [])
            for idx, comp_id in enumerate(order, start=1):
                db.session.query(model).filter(
                    model.id == comp_id,
                    getattr(model, parent_field) == parent_id
                ).update({'order_no': idx})
            db.session.commit()
            return jsonify({'success': True})

        return jsonify({'success': False, 'message': 'Invalid action'}), 400

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Component API error: {str(e)}")
        return jsonify({'success': False, 'message': 'Server error'}), 500