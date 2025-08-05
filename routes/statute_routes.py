from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app
from sqlalchemy.exc import SQLAlchemyError
from models import db, Statute, Annotation
from forms import StatuteForm
from database import check_exists, save_with_transaction, get_full_hierarchy
from datetime import datetime
import pytz
import re 
from flask_login import login_required
statute_bp = Blueprint('statute', __name__, url_prefix='/statute')

@login_required
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
        
        # Paginate results - using error_out=False to prevent 404 on invalid page
        statutes = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        # If no results and page > 1, redirect to page 1
        if not statutes.items and page > 1:
            return redirect(url_for('statute.list_statutes', search=search))
        
        return render_template('statute/list.html', statutes=statutes, search=search)
        
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Database error listing statutes: {str(e)}")
        flash("A database error occurred while retrieving statutes.", "danger")
        return redirect(url_for('index'))
    except Exception as e:
        current_app.logger.error(f"Error listing statutes: {str(e)}")
        flash("An error occurred while retrieving statutes.", "danger")
        return redirect(url_for('index'))

@login_required
@statute_bp.route('/<int:statute_id>/book-view', methods=['GET'])
def book_view(statute_id):
    """View statute in book/PDF-like format"""
    try:
        # Get the statute
        statute = db.session.query(Statute).filter(Statute.id == statute_id).first()
        
        if not statute:
            flash("Statute not found.", "danger")
            return redirect(url_for('statute.list_statutes'))
        
        # Get the full hierarchy for this statute
        hierarchy = get_full_hierarchy(statute_id)
        
        if not hierarchy:
            flash("Error loading statute content.", "danger")
            return redirect(url_for('statute.view_statute', statute_id=statute_id))
        
        # Process annotations in the content
        processed_hierarchy = process_hierarchy_annotations(hierarchy, statute_id)
        
        return render_template(
            'statute/book_view.html',
            statute=statute,
            hierarchy=processed_hierarchy
        )
        
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Database error in book view: {str(e)}")
        flash("A database error occurred while retrieving the statute.", "danger")
        return redirect(url_for('statute.view_statute', statute_id=statute_id))
    except Exception as e:
        current_app.logger.error(f"Error in book view: {str(e)}")
        flash("An error occurred while retrieving the statute.", "danger")
        return redirect(url_for('statute.view_statute', statute_id=statute_id))

def process_hierarchy_annotations(hierarchy, statute_id):
    """Process annotations throughout the entire hierarchy"""
    processed = hierarchy.copy()
    
    if processed['statute'].get('name'):
        processed['statute']['name'], _ = process_annotations(
            processed['statute']['name'], statute_id
        )
    if processed['statute'].get('act_no'):
        processed['statute']['act_no'], _ = process_annotations(
            processed['statute']['act_no'], statute_id
        )
    if processed['statute'].get('date'):
        processed['statute']['date'], _ = process_annotations(
            processed['statute']['date'], statute_id
        )
    # Process statute preface
    if processed['statute'].get('preface'):
        processed['statute']['preface'], _ = process_annotations(
            processed['statute']['preface'], statute_id
        )
    
    # Process parts
    for part in processed.get('parts', []):
        # Process part name (skip if pseudo)
        if part.get('part_no') and part['part_no'].lower() != 'pseudo':
            part['part_no'], _ = process_annotations(part['part_no'], statute_id)
        if part.get('name') and part['name'].lower() != 'pseudo':
            part['name'], _ = process_annotations(part['name'], statute_id)
        
        # Process chapters
        for chapter in part.get('chapters', []):
            if chapter.get('chapter_no') and chapter['chapter_no'].lower() != 'pseudo':
                chapter['chapter_no'], _ = process_annotations(chapter['chapter_no'], statute_id)
            if chapter.get('name') and chapter['name'].lower() != 'pseudo':
                chapter['name'], _ = process_annotations(chapter['name'], statute_id)
            
            # Process sets
            for set_item in chapter.get('sets', []):
                if set_item.get('set_no') and set_item['set_no'].lower() != 'pseudo':
                    set_item['set_no'], _ = process_annotations(set_item['set_no'], statute_id)
                if set_item.get('name') and set_item['name'].lower() != 'pseudo':
                    set_item['name'], _ = process_annotations(set_item['name'], statute_id)
                
                # Process sections
                for section in set_item.get('sections', []):
                    print(section.get('section_no'))
                    if section.get('section_no') and section['section_no'].lower() != 'pseudo':
                        section['section_no'], _ = process_annotations(section['section_no'], statute_id)
                    if section.get('name') and section['name'].lower() != 'pseudo':
                        section['name'], _ = process_annotations(section['name'], statute_id)
                    
                    # Process subsections
                    for subsection in section.get('subsections', []):
                        if subsection.get('subsection_no') and subsection['subsection_no'].lower() != 'pseudo':
                            subsection['subsection_no'], _ = process_annotations(subsection['subsection_no'], statute_id)
                        if subsection.get('name') and subsection['name'].lower() != 'pseudo':
                            subsection['name'], _ = process_annotations(subsection['name'], statute_id)
                        
                        if subsection.get('content'):
                            subsection['content'], _ = process_annotations(subsection['content'], statute_id)
    
    # Process schedule parts (similar structure)
    for sch_part in processed.get('sch_parts', []):
        if sch_part.get('name') and sch_part['name'].lower() != 'pseudo':
            sch_part['name'], _ = process_annotations(sch_part['name'], statute_id)
        
        for sch_chapter in sch_part.get('sch_chapters', []):
            if sch_chapter.get('name') and sch_chapter['name'].lower() != 'pseudo':
                sch_chapter['name'], _ = process_annotations(sch_chapter['name'], statute_id)
            
            for sch_set in sch_chapter.get('sch_sets', []):
                if sch_set.get('name') and sch_set['name'].lower() != 'pseudo':
                    sch_set['name'], _ = process_annotations(sch_set['name'], statute_id)
                
                for sch_section in sch_set.get('sch_sections', []):
                    if sch_section.get('name') and sch_section['name'].lower() != 'pseudo':
                        sch_section['name'], _ = process_annotations(sch_section['name'], statute_id)
                    
                    for sch_subsection in sch_section.get('sch_subsections', []):
                        if sch_subsection.get('name') and sch_subsection['name'].lower() != 'pseudo':
                            sch_subsection['name'], _ = process_annotations(sch_subsection['name'], statute_id)
                        
                        if sch_subsection.get('content'):
                            sch_subsection['content'], _ = process_annotations(sch_subsection['content'], statute_id)
    
    return processed

def process_annotations(text, statute_id):
    """
    Process annotation tags in text and convert them to formatted text with tooltips.
    Handles both <fa> (full annotation) and <pa> (partial annotation) tags.
    Supports nested tags.
    """
    if not text:
        return text, []
    
    # Get all annotations for this statute
    annotations = {}
    try:
        statute_annotations = db.session.query(Annotation).filter(
            Annotation.statute_id == statute_id
        ).all()
        
        for ann in statute_annotations:
            key = f"{ann.no}_{ann.page_no}" if ann.page_no else ann.no
            annotations[key] = ann.footnote
    except Exception as e:
        current_app.logger.error(f"Error fetching annotations: {str(e)}")
    
    processed_text = text
    footnotes = []
    
    # Pattern to match both fa and pa tags with their attributes
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
        
        # Process nested annotations recursively
        processed_content, nested_footnotes = process_annotations(content, statute_id)
        footnotes.extend(nested_footnotes)
        
        # Create formatted text with superscript and tooltip
        formatted = f'<span class="annotated-text" title="{footnote_text}" data-annotation="{a_value}"><sup class="annotation-number">{a_value}</sup>[{processed_content}]</span>'
        
        # Add to footnotes list
        footnotes.append({
            'number': a_value,
            'page': p_value,
            'text': footnote_text,
            'type': tag_type
        })
        
        return formatted
    
    # Process all annotation tags
    while re.search(pattern, processed_text, re.DOTALL):
        processed_text = re.sub(pattern, replace_annotation, processed_text, flags=re.DOTALL)
    
    return processed_text, footnotes

@statute_bp.route('/new', methods=['GET', 'POST'])
@login_required
def add_statute():
    """Add a new statute"""
    form = StatuteForm()
    
    if request.method == 'POST' and form.validate_on_submit():
        try:
            # Check if statute with same name already exists
            existing = check_exists(Statute, name=form.name.data)
            print(existing, '=======================================')
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
                
        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Database error adding statute: {str(e)}")
            flash("A database error occurred while creating the statute.", "danger")
        except Exception as e:
            current_app.logger.error(f"Error adding statute: {str(e)}")
            flash("An error occurred while creating the statute.", "danger")
    
    return render_template('statute/add.html', form=form)

@statute_bp.route('/<int:statute_id>', methods=['GET'])
@login_required
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
        
        return render_template(
            'statute/view.html', 
            statute=statute, 
            parts=hierarchy.get('parts', []) if hierarchy else [],
            sch_parts=hierarchy.get('sch_parts', []) if hierarchy else []
        )
        
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Database error viewing statute: {str(e)}")
        flash("A database error occurred while retrieving the statute.", "danger")
        return redirect(url_for('statute.list_statutes'))
    except Exception as e:
        current_app.logger.error(f"Error viewing statute: {str(e)}")
        flash("An error occurred while retrieving the statute.", "danger")
        return redirect(url_for('statute.list_statutes'))

@statute_bp.route('/<int:statute_id>/edit', methods=['GET', 'POST'])
@login_required
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
        
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Database error editing statute: {str(e)}")
        flash("A database error occurred while editing the statute.", "danger")
        return redirect(url_for('statute.list_statutes'))
    except Exception as e:
        current_app.logger.error(f"Error editing statute: {str(e)}")
        flash("An error occurred while editing the statute.", "danger")
        return redirect(url_for('statute.list_statutes'))

@statute_bp.route('/<int:statute_id>/delete', methods=['POST'])
@login_required
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