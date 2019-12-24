import re
import decimal

from flask import current_app

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_ckeditor import CKEditorField

from wtforms import StringField, PasswordField, BooleanField, SubmitField, HiddenField, SelectField, RadioField, DecimalField
from wtforms.fields.html5 import DateField
from wtforms.fields import FieldList, FormField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length, Regexp

#from wtforms.widgets import TextArea

from wtforms import Form

from wtforms_alchemy import model_form_factory

from app.models import User, CpdActivityEntry

'''
BaseModelForm = model_form_factory(FlaskForm)

class ModelForm(BaseModelForm):
    @classmethod
    def get_session(self):
        return db.session
'''

class LoginForm(FlaskForm):

    #username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class PageForm(FlaskForm):

    id = HiddenField('id')
    title = StringField('Title', validators=[DataRequired(), Length(max=100)])
    content = CKEditorField('Write something')
    #tags = StringField('Tags')
    url = StringField('Url', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Submit')

class PersonDetailForm(FlaskForm):

    id = HiddenField('id')
    title = SelectField(
        'Title',
        choices=[('Mr', 'Mr'), ('Ms', 'Ms'), ('Mrs', 'Mrs'), ('Prof', 'Prof'), ('Dr', 'Dr')]
    )
    date_of_birth = DateField('Date of birth', format='%Y-%m-%d')
    country_of_birth = StringField('Country Of Birth')

    name_of_registrant = StringField('Name of Registrant', validators=[DataRequired()])
    chinese_name = StringField('Chinese Name')
    online_id = StringField('Online ID')
    #online_registration_date = db.Column(db.DateTime)
    #email = db.Column(db.String(100), index=True, unique=True)
    mobile_phone = StringField('Mobile Phone', validators=[DataRequired()])
    office_phone = StringField('Office Phone')
    correspondence_addr = StringField('Correspondence Address', validators=[DataRequired()])
    work_addr = StringField('Work Address')

class LangCompetenceForm(FlaskForm):

    lang_competence_id = HiddenField('id')
    dominant_lang = RadioField('Your Dominant Language(s)', choices=[('C','Cantonese'),('E','English'),('P','Putonghua')])
    dominant_lang_other = StringField('Other')

    lang_training_was_conducted = RadioField('The language(s) in which your therapy training was conducted', choices=[('C','Cantonese'),('E','English'),('P','Putonghua')])
    lang_training_was_conducted_other = StringField('Other')

    lang_provide_therapy = RadioField('The language(s) in which your will provide speech therapy', choices=[('C','Cantonese'),('E','English'),('P','Putonghua')])
    lang_provide_therapy_other = StringField('Other')

class LangCompetenceEntriesForm(FlaskForm):

    lang_competence_entries = FieldList(FormField(LangCompetenceForm), min_entries=0, max_entries=3)

class ProfessionalQualificationForm(FlaskForm):

    professional_qualification_id = HiddenField('id')
    qualification_name = StringField('Qualification Name', validators=[DataRequired()])
    issue_authority = StringField('Issue Authority', validators=[DataRequired()])
    issue_year = StringField('Issue Year', validators=[DataRequired()])

    qualification_name_in_eng = StringField('Qualification Name in English')
    issue_authority_in_eng = StringField('Issue Authority in English')

    country_name = StringField('Country Name')
    language_of_instruction= StringField('Language of Instruction')
    graduation_date = DateField('Graduation Date', format='%Y-%m-%d')
    level = StringField('Level')

    #upload_file = FileField('Upload File', validators=[FileAllowed(['png', 'pdf', 'jpg'], "wrong format!")])

class ProfessionalQualificationEntriesForm(FlaskForm):

    professional_qualification_entries = FieldList(FormField(ProfessionalQualificationForm), min_entries=0, max_entries=3)


class ProfessionalRecognitionForm(FlaskForm):

    professional_recognition_id = HiddenField('id')
    country_name = StringField('Country Name', validators=[DataRequired()])
    organization_name = StringField('Organization Name', validators=[DataRequired()])
    membership_type = StringField('Membership Type')
    expiry_date = DateField('Expiry Date', format='%Y-%m-%d')

    
class ProfessionalRecognitionEntriesForm(FlaskForm):

    professional_recognition_entries = FieldList(FormField(ProfessionalRecognitionForm), min_entries=0, max_entries=3)


class WorkExperienceForm(FlaskForm):

    work_experience_id = HiddenField('id')
    employer_name = StringField('Employer Name', validators=[DataRequired()])
    job_title = StringField('Job Title', validators=[DataRequired()])
    from_date = DateField('Start Date', format='%Y-%m-%d', validators=[DataRequired()])
    to_date = DateField('End Date', format='%Y-%m-%d')


class WorkExperienceEntriesForm(FlaskForm):

    work_experience_entries = FieldList(FormField(WorkExperienceForm), min_entries=0, max_entries=3)


class SignUpForm(FlaskForm):

    #username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    '''
    def validate_email(self, email):

        #if submit is not None :

        #current_app.logger.debug(submit.data)

        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')
    '''

    def validate_password(self, password):
        matchObj = re.search("^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{6,8}$", password.data)

        if matchObj is None:
            raise ValidationError('Must contain at least 1 digit, 1 small letter and 1 capital letter and between 6-8 characters')


class AskQuestionForm(FlaskForm):
    answer = DateField('What is you birthday ?', format='%Y-%m-%d', validators=[DataRequired()])
 

class ResetPasswordForm(FlaskForm):
    signUp = FormField(SignUpForm)
    askQuestion = FormField(AskQuestionForm)


class CpdActivityEntryForm(FlaskForm):
#class CpdActivityEntryForm(ModelForm):

  
    #activity_description = StringField('Description', validators=[DataRequired()])

    #id = HiddenField('id')
    cpd_activity_entry_id = HiddenField('id')

    activity_description = TextAreaField('Description')

    point_awarded = DecimalField('Point awarded', places=1, rounding=None)

    cpd_activity_id = HiddenField('cpd_actvity_id')

    category = StringField('Category') #foreign key 

    
    '''
    class Meta:
        model = CpdActivityEntry
    '''

class CpdActivityEntriesForm(FlaskForm):

    cpd_activity_entries = FieldList(FormField(CpdActivityEntryForm), min_entries=0)

class UploadForm(FlaskForm):
    #photo = FileField(validators=[FileRequired()])
    photo = FileField()

    #print('debug')
    #print (photo.filename)

    '''
    def validate_photo(self, photo):

        print('debug')
        print (photo.filename)

        if not '.' in photo.filename and \
           photo.filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS:
        
             raise ValidationError('The file type is not allowed!')
    '''

class UploadEntriesForm(FlaskForm):

    upload_entries = FieldList(FormField(UploadForm), min_entries=0, max_entries=3)