from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from flask import current_app
from models import db, Statute, Part, Chapter, Set, Section, Subsection, Annotation
from models import SchPart, SchChapter, SchSet, SchSection, SchSubsection
        
def check_exists(model, **kwargs):
    """
    Check if a record already exists to prevent duplicates
    
    Args:
        model: SQLAlchemy model class
        **kwargs: Parameters to filter by
        
    Returns:
        Record if exists, None otherwise
    """
    try:
        return db.session.query(model).filter_by(**kwargs).first()
    except SQLAlchemyError as e:
        current_app.logger.error(f"Error checking existence: {str(e)}")
        return None

def get_next_order_no(parent_id, model, parent_field):
    """
    Get the next order number for hierarchical items
    
    Args:
        parent_id: ID of the parent record
        model: SQLAlchemy model class
        parent_field: Field name for the parent reference
        
    Returns:
        Next order number (int)
    """
    try:
        # Query for the highest existing order_no and increment by 1
        highest = db.session.query(db.func.max(model.order_no)).filter(
            getattr(model, parent_field) == parent_id
        ).scalar()
        
        # If no records exist yet, start with 1
        if highest is None:
            return 1
            
        return highest + 1
    except SQLAlchemyError as e:
        current_app.logger.error(f"Error getting next order number: {str(e)}")
        return 1  # Default to 1 if there's an error
        
def save_with_transaction(item):
    """
    Save an item using database transaction to prevent data corruption
    
    Args:
        item: SQLAlchemy model instance to save
        
    Returns:
        Tuple (success, message)
    """
    try:
        # Add and flush to get ID if necessary
        db.session.add(item)
        db.session.flush()
        
        # Commit the transaction
        db.session.commit()
        
        return True, f"Successfully saved {item.__class__.__name__} with ID {item.id}"
    except IntegrityError as e:
        # Roll back on integrity errors (duplicate entries, etc.)
        db.session.rollback()
        
        error_msg = str(e)
        
        if 'unique constraint' in error_msg.lower():
            return False, "A duplicate entry already exists. Please check your input."
        
        current_app.logger.error(f"Integrity error: {error_msg}")
        return False, "Could not save due to data integrity error."
    except SQLAlchemyError as e:
        # Roll back on other database errors
        db.session.rollback()
        
        current_app.logger.error(f"Database error: {str(e)}")
        return False, "Could not save due to a database error."
    except Exception as e:
        # Roll back on unexpected errors
        db.session.rollback()
        
        current_app.logger.error(f"Unexpected error: {str(e)}")
        return False, "Could not save due to an unexpected error."

def get_full_hierarchy(statute_id):
    """
    Get the full hierarchy of a statute for display
    
    Args:
        statute_id: ID of the statute
        
    Returns:
        Dictionary with full hierarchy information
    """
    try:
        # Get the statute
        statute = db.session.query(Statute).filter(Statute.id == statute_id).first()
        if not statute:
            return None
        
        # Get all parts with their children, ordered by order_no
        parts = (db.session.query(Part)
                .filter(Part.statute_id == statute_id)
                .order_by(Part.order_no)
                .all())
        
        parts_data = []
        for part in parts:
            chapters = (db.session.query(Chapter)
                       .filter(Chapter.part_id == part.id)
                       .order_by(Chapter.order_no)
                       .all())
            
            chapters_data = []
            for chapter in chapters:
                sets = (db.session.query(Set)
                       .filter(Set.chapter_id == chapter.id)
                       .order_by(Set.order_no)
                       .all())
                
                sets_data = []
                for set_item in sets:
                    sections = (db.session.query(Section)
                              .filter(Section.set_id == set_item.id)
                              .order_by(Section.order_no)
                              .all())
                    
                    sections_data = []
                    for section in sections:
                        subsections = (db.session.query(Subsection)
                                     .filter(Subsection.section_id == section.id)
                                     .order_by(Subsection.order_no)
                                     .all())
                        
                        subsections_data = [subsection.to_dict() for subsection in subsections]
                        
                        section_dict = section.to_dict()
                        section_dict['subsections'] = subsections_data
                        sections_data.append(section_dict)
                    
                    set_dict = set_item.to_dict()
                    set_dict['sections'] = sections_data
                    sets_data.append(set_dict)
                
                chapter_dict = chapter.to_dict()
                chapter_dict['sets'] = sets_data
                chapters_data.append(chapter_dict)
            
            part_dict = part.to_dict()
            part_dict['chapters'] = chapters_data
            parts_data.append(part_dict)
        
        # Get all schedule parts with their children, ordered by order_no
        sch_parts = (db.session.query(SchPart)
                    .filter(SchPart.statute_id == statute_id)
                    .order_by(SchPart.order_no)
                    .all())
        
        sch_parts_data = []
        for sch_part in sch_parts:
            sch_chapters = (db.session.query(SchChapter)
                           .filter(SchChapter.sch_part_id == sch_part.id)
                           .order_by(SchChapter.order_no)
                           .all())
            
            sch_chapters_data = []
            for sch_chapter in sch_chapters:
                sch_sets = (db.session.query(SchSet)
                           .filter(SchSet.sch_chapter_id == sch_chapter.id)
                           .order_by(SchSet.order_no)
                           .all())
                
                sch_sets_data = []
                for sch_set in sch_sets:
                    sch_sections = (db.session.query(SchSection)
                                  .filter(SchSection.sch_set_id == sch_set.id)
                                  .order_by(SchSection.order_no)
                                  .all())
                    
                    sch_sections_data = []
                    for sch_section in sch_sections:
                        sch_subsections = (db.session.query(SchSubsection)
                                         .filter(SchSubsection.sch_section_id == sch_section.id)
                                         .order_by(SchSubsection.order_no)
                                         .all())
                        
                        sch_subsections_data = [sch_subsection.to_dict() for sch_subsection in sch_subsections]
                        
                        sch_section_dict = sch_section.to_dict()
                        sch_section_dict['sch_subsections'] = sch_subsections_data
                        sch_sections_data.append(sch_section_dict)
                    
                    sch_set_dict = sch_set.to_dict()
                    sch_set_dict['sch_sections'] = sch_sections_data
                    sch_sets_data.append(sch_set_dict)
                
                sch_chapter_dict = sch_chapter.to_dict()
                sch_chapter_dict['sch_sets'] = sch_sets_data
                sch_chapters_data.append(sch_chapter_dict)
            
            sch_part_dict = sch_part.to_dict()
            sch_part_dict['sch_chapters'] = sch_chapters_data
            sch_parts_data.append(sch_part_dict)
        
        # Return the complete hierarchy
        return {
            'statute': statute.to_dict(),
            'parts': parts_data,
            'sch_parts': sch_parts_data
        }
        
    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f"Database error getting hierarchy: {str(e)}")
        return None
    except Exception as e:
        current_app.logger.error(f"Error getting hierarchy: {str(e)}")
        return None

def delete_with_transaction(item):
    """
    Delete an item using database transaction
    
    Args:
        item: SQLAlchemy model instance to delete
        
    Returns:
        Tuple (success, message)
    """
    try:
        # Delete the item
        db.session.delete(item)
        
        # Commit the transaction
        db.session.commit()
        
        return True, f"Successfully deleted {item.__class__.__name__}"
    except SQLAlchemyError as e:
        # Roll back on database errors
        db.session.rollback()
        
        current_app.logger.error(f"Database error during deletion: {str(e)}")
        return False, "Could not delete due to a database error."
    except Exception as e:
        # Roll back on unexpected errors
        db.session.rollback()
        
        current_app.logger.error(f"Unexpected error during deletion: {str(e)}")
        return False, "Could not delete due to an unexpected error."