from flask_wtf import FlaskForm
from wtforms import StringField, DateField, TextAreaField, IntegerField, HiddenField
from wtforms.validators import DataRequired, Optional, Length

class StatuteForm(FlaskForm):
    """Form for adding/editing statutes"""
    name = StringField('Name', validators=[DataRequired(), Length(max=255)])
    act_no = StringField('Act Number', validators=[Optional(), Length(max=100)])
    date = DateField('Date', validators=[Optional()], format='%Y-%m-%d')
    preface = TextAreaField('Preface', validators=[Optional()])

class PartForm(FlaskForm):
    """Form for adding/editing parts"""
    name = StringField('Name', validators=[DataRequired(), Length(max=255)])
    part_no = StringField('Part Number', validators=[Optional(), Length(max=100)])
    order_no = IntegerField('Order Number', validators=[Optional()])
    statute_id = HiddenField('Statute ID', validators=[DataRequired()])

class ChapterForm(FlaskForm):
    """Form for adding/editing chapters"""
    name = StringField('Name', validators=[DataRequired(), Length(max=255)])
    chapter_no = StringField('Chapter Number', validators=[Optional(), Length(max=100)])
    order_no = IntegerField('Order Number', validators=[Optional()])
    part_id = HiddenField('Part ID', validators=[DataRequired()])

class SetForm(FlaskForm):
    """Form for adding/editing sets"""
    name = StringField('Name', validators=[DataRequired(), Length(max=255)])
    set_no = StringField('Set Number', validators=[Optional(), Length(max=100)])
    order_no = IntegerField('Order Number', validators=[Optional()])
    chapter_id = HiddenField('Chapter ID', validators=[DataRequired()])

class SectionForm(FlaskForm):
    """Form for adding/editing sections"""
    name = StringField('Name', validators=[DataRequired(), Length(max=255)])
    section_no = StringField('Section Number', validators=[Optional(), Length(max=100)])
    order_no = IntegerField('Order Number', validators=[Optional()])
    set_id = HiddenField('Set ID', validators=[DataRequired()])

class SubsectionForm(FlaskForm):
    """Form for adding/editing subsections"""
    name = StringField('Name', validators=[Optional(), Length(max=255)])
    subsection_no = StringField('Subsection Number', validators=[Optional(), Length(max=100)])
    content = TextAreaField('Content', validators=[DataRequired()])
    order_no = IntegerField('Order Number', validators=[Optional()])
    section_id = HiddenField('Section ID', validators=[DataRequired()])

class AnnotationForm(FlaskForm):
    """Form for adding/editing annotations"""
    no = StringField('Annotation Number', validators=[DataRequired(), Length(max=100)])
    page_no = StringField('Page Number', validators=[Optional(), Length(max=100)])
    footnote = TextAreaField('Footnote', validators=[DataRequired()])
    statute_id = HiddenField('Statute ID', validators=[DataRequired()])

# Forms for schedule components
class SchPartForm(FlaskForm):
    """Form for adding/editing schedule parts"""
    name = StringField('Name', validators=[DataRequired(), Length(max=255)])
    part_no = StringField('Part Number', validators=[Optional(), Length(max=100)])
    order_no = IntegerField('Order Number', validators=[Optional()])
    statute_id = HiddenField('Statute ID', validators=[DataRequired()])

class SchChapterForm(FlaskForm):
    """Form for adding/editing schedule chapters"""
    name = StringField('Name', validators=[DataRequired(), Length(max=255)])
    chapter_no = StringField('Chapter Number', validators=[Optional(), Length(max=100)])
    order_no = IntegerField('Order Number', validators=[Optional()])
    sch_part_id = HiddenField('Schedule Part ID', validators=[DataRequired()])

class SchSetForm(FlaskForm):
    """Form for adding/editing schedule sets"""
    name = StringField('Name', validators=[DataRequired(), Length(max=255)])
    set_no = StringField('Set Number', validators=[Optional(), Length(max=100)])
    order_no = IntegerField('Order Number', validators=[Optional()])
    sch_chapter_id = HiddenField('Schedule Chapter ID', validators=[DataRequired()])

class SchSectionForm(FlaskForm):
    """Form for adding/editing schedule sections"""
    name = StringField('Name', validators=[DataRequired(), Length(max=255)])
    section_no = StringField('Section Number', validators=[Optional(), Length(max=100)])
    order_no = IntegerField('Order Number', validators=[Optional()])
    sch_set_id = HiddenField('Schedule Set ID', validators=[DataRequired()])

class SchSubsectionForm(FlaskForm):
    """Form for adding/editing schedule subsections"""
    name = StringField('Name', validators=[Optional(), Length(max=255)])
    subsection_no = StringField('Subsection Number', validators=[Optional(), Length(max=100)])
    content = TextAreaField('Content', validators=[DataRequired()])
    order_no = IntegerField('Order Number', validators=[Optional()])
    sch_section_id = HiddenField('Schedule Section ID', validators=[DataRequired()])