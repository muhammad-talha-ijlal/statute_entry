from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz

from extensions import db
from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = "user"
    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)   # store a hash

    # convenience helpers
    def set_password(self, raw_pwd):
        self.password = raw_pwd
    def check_password(self, raw_pwd):
        return self.password == raw_pwd

class Log(db.Model):
    __tablename__ = "log"
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey("user.id"))
    table_name = db.Column(db.String(50), nullable=False)
    record_id  = db.Column(db.Integer, nullable=False)
    action     = db.Column(db.String(10), nullable=False)   # INSERT / UPDATE / DELETE
    timestamp  = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC))


class Statute(db.Model):
    """Statute model corresponding to statute table in schema"""
    __tablename__ = 'statute'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False, unique=True)
    act_no = db.Column(db.Text, unique=True)
    date = db.Column(db.Date)
    preface = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC))
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), 
                           onupdate=lambda: datetime.now(pytz.UTC))
    
    # Relationships
    parts = db.relationship('Part', backref='statute', cascade='all, delete-orphan')
    sch_parts = db.relationship('SchPart', backref='statute', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Statute {self.name}>'
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'act_no': self.act_no,
            'date': self.date.isoformat() if self.date else None,
            'preface': self.preface,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Part(db.Model):
    """Part model corresponding to part table in schema"""
    __tablename__ = 'part'
    
    id = db.Column(db.Integer, primary_key=True)
    statute_id = db.Column(db.Integer, db.ForeignKey('statute.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.Text, nullable=False)
    part_no = db.Column(db.Text)
    order_no = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC))
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), 
                           onupdate=lambda: datetime.now(pytz.UTC))
    
    # Relationships
    chapters = db.relationship('Chapter', backref='part', cascade='all, delete-orphan')
    
    __table_args__ = (
        db.UniqueConstraint('statute_id', 'order_no', name='uq_part_statute_order'),
    )
    
    def __repr__(self):
        return f'<Part {self.name}>'
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'statute_id': self.statute_id,
            'name': self.name,
            'part_no': self.part_no,
            'order_no': self.order_no,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Chapter(db.Model):
    """Chapter model corresponding to chapter table in schema"""
    __tablename__ = 'chapter'
    
    id = db.Column(db.Integer, primary_key=True)
    part_id = db.Column(db.Integer, db.ForeignKey('part.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.Text, nullable=False)
    chapter_no = db.Column(db.Text)
    order_no = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC))
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), 
                           onupdate=lambda: datetime.now(pytz.UTC))
    
    # Relationships
    sets = db.relationship('Set', backref='chapter', cascade='all, delete-orphan')
    
    __table_args__ = (
        db.UniqueConstraint('part_id', 'order_no', name='uq_chapter_part_order'),
    )
    
    def __repr__(self):
        return f'<Chapter {self.name}>'
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'part_id': self.part_id,
            'name': self.name,
            'chapter_no': self.chapter_no,
            'order_no': self.order_no,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Set(db.Model):
    """Set model corresponding to set table in schema"""
    __tablename__ = 'set'
    
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapter.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.Text, nullable=False)
    set_no = db.Column(db.Text)
    order_no = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC))
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), 
                           onupdate=lambda: datetime.now(pytz.UTC))
    
    # Relationships
    sections = db.relationship('Section', backref='set', cascade='all, delete-orphan')
    
    __table_args__ = (
        db.UniqueConstraint('chapter_id', 'order_no', name='uq_set_chapter_order'),
    )
    
    def __repr__(self):
        return f'<Set {self.name}>'
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'chapter_id': self.chapter_id,
            'name': self.name,
            'set_no': self.set_no,
            'order_no': self.order_no,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Section(db.Model):
    """Section model corresponding to section table in schema"""
    __tablename__ = 'section'
    
    id = db.Column(db.Integer, primary_key=True)
    set_id = db.Column(db.Integer, db.ForeignKey('set.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.Text, nullable=False)
    section_no = db.Column(db.Text)
    order_no = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC))
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), 
                           onupdate=lambda: datetime.now(pytz.UTC))
    
    # Relationships
    subsections = db.relationship('Subsection', backref='section', cascade='all, delete-orphan')
    
    __table_args__ = (
        db.UniqueConstraint('set_id', 'order_no', name='uq_section_set_order'),
    )
    
    def __repr__(self):
        return f'<Section {self.name}>'
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'set_id': self.set_id,
            'name': self.name,
            'section_no': self.section_no,
            'order_no': self.order_no,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Subsection(db.Model):
    """Subsection model corresponding to subsection table in schema"""
    __tablename__ = 'subsection'
    
    id = db.Column(db.Integer, primary_key=True)
    section_id = db.Column(db.Integer, db.ForeignKey('section.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.Text)
    subsection_no = db.Column(db.Text)
    content = db.Column(db.Text, nullable=False)
    order_no = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC))
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), 
                           onupdate=lambda: datetime.now(pytz.UTC))
    
    __table_args__ = (
        db.UniqueConstraint('section_id', 'order_no', name='uq_subsection_section_order'),
    )
    
    def __repr__(self):
        return f'<Subsection {self.name}>'
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'section_id': self.section_id,
            'name': self.name,
            'subsection_no': self.subsection_no,
            'content': self.content,
            'order_no': self.order_no,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class Annotation(db.Model):
    """Annotation model corresponding to annotation table in schema"""
    __tablename__ = 'annotation'
    
    id = db.Column(db.Integer, primary_key=True)
    no = db.Column(db.Text, nullable=False)
    page_no = db.Column(db.Text)
    statute_id = db.Column(db.Integer, db.ForeignKey('statute.id', ondelete='CASCADE'))
    footnote = db.Column(db.Text)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC))
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), 
                           onupdate=lambda: datetime.now(pytz.UTC))
    
    
    def __repr__(self):
        return f'<Annotation {self.no}>'
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'no': self.no,
            'statute_id': self.statute_id,
            'page_no': self.page_no,
            'footnote': self.footnote,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

# Schedule-related models
class SchPart(db.Model):
    """Schedule Part model corresponding to sch_part table in schema"""
    __tablename__ = 'sch_part'
    
    id = db.Column(db.Integer, primary_key=True)
    statute_id = db.Column(db.Integer, db.ForeignKey('statute.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.Text, nullable=False)
    part_no = db.Column(db.Text)
    order_no = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC))
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), 
                           onupdate=lambda: datetime.now(pytz.UTC))
    
    # Relationships
    sch_chapters = db.relationship('SchChapter', backref='sch_part', cascade='all, delete-orphan')
    
    __table_args__ = (
        db.UniqueConstraint('statute_id', 'order_no', name='uq_sch_part_statute_order'),
    )
    
    def __repr__(self):
        return f'<SchPart {self.name}>'
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            'id': self.id,
            'statute_id': self.statute_id,
            'name': self.name,
            'part_no': self.part_no,
            'order_no': self.order_no,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class SchChapter(db.Model):
    """Schedule Chapter model corresponding to sch_chapter table in schema"""
    __tablename__ = 'sch_chapter'
    
    id = db.Column(db.Integer, primary_key=True)
    sch_part_id = db.Column(db.Integer, db.ForeignKey('sch_part.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.Text, nullable=False)
    chapter_no = db.Column(db.Text)
    order_no = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC))
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), 
                           onupdate=lambda: datetime.now(pytz.UTC))
    
    # Relationships
    sch_sets = db.relationship('SchSet', backref='sch_chapter', cascade='all, delete-orphan')
    
    __table_args__ = (
        db.UniqueConstraint('sch_part_id', 'order_no', name='uq_sch_chapter_part_order'),
    )
    
    def __repr__(self):
        return f'<SchChapter {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'order_no': self.order_no,
            'sch_part_id': self.sch_part_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class SchSet(db.Model):
    """Schedule Set model corresponding to sch_set table in schema"""
    __tablename__ = 'sch_set'
    
    id = db.Column(db.Integer, primary_key=True)
    sch_chapter_id = db.Column(db.Integer, db.ForeignKey('sch_chapter.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.Text, nullable=False)
    set_no = db.Column(db.Text)
    order_no = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC))
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), 
                           onupdate=lambda: datetime.now(pytz.UTC))
    
    # Relationships
    sch_sections = db.relationship('SchSection', backref='sch_set', cascade='all, delete-orphan')
    
    __table_args__ = (
        db.UniqueConstraint('sch_chapter_id', 'order_no', name='uq_sch_set_chapter_order'),
    )
    
    def __repr__(self):
        return f'<SchSet {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'order_no': self.order_no,
            'sch_chapter_id': self.sch_chapter_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class SchSection(db.Model):
    """Schedule Section model corresponding to sch_section table in schema"""
    __tablename__ = 'sch_section'
    
    id = db.Column(db.Integer, primary_key=True)
    sch_set_id = db.Column(db.Integer, db.ForeignKey('sch_set.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.Text, nullable=False)
    section_no = db.Column(db.Text)
    order_no = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC))
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), 
                           onupdate=lambda: datetime.now(pytz.UTC))
    
    # Relationships
    sch_subsections = db.relationship('SchSubsection', backref='sch_section', cascade='all, delete-orphan')
    
    __table_args__ = (
        db.UniqueConstraint('sch_set_id', 'order_no', name='uq_sch_section_set_order'),
    )
    
    def __repr__(self):
        return f'<SchSection {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'order_no': self.order_no,
            'sch_set_id': self.sch_set_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class SchSubsection(db.Model):
    """Schedule Subsection model corresponding to sch_subsection table in schema"""
    __tablename__ = 'sch_subsection'
    
    id = db.Column(db.Integer, primary_key=True)
    sch_section_id = db.Column(db.Integer, db.ForeignKey('sch_section.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.Text)
    subsection_no = db.Column(db.Text)
    content = db.Column(db.Text, nullable=False)
    order_no = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC))
    updated_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), 
                           onupdate=lambda: datetime.now(pytz.UTC))
    
    __table_args__ = (
        db.UniqueConstraint('sch_section_id', 'order_no', name='uq_sch_subsection_section_order'),
    )
    
    def __repr__(self):
        return f'<SchSubsection {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'order_no': self.order_no,
            'sch_section_id': self.sch_section_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

from sqlalchemy import event
from flask_login import current_user

def _log_action(mapper, connection, target, action):
    # skip if the model *is* the Log table
    if target.__tablename__ == "log":
        return
    try:
        user_id = current_user.get_id() if current_user.is_authenticated else None
    except RuntimeError:
        user_id = None  # outside request ctx (e.g. CLI)
    connection.execute(
        Log.__table__.insert().values(
            user_id=user_id,
            table_name=target.__tablename__,
            record_id=getattr(target, "id", None),
            action=action
        )
    )

for act, sa_event in [("INSERT", "after_insert"),
                      ("UPDATE", "after_update"),
                      ("DELETE", "after_delete")]:
    event.listen(db.Model, sa_event,
                 lambda mapper, conn, tgt, a=act: _log_action(mapper, conn, tgt, a),
                 propagate=True)
