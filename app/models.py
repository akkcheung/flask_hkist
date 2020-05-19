
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import orm

from app import db, login

import datetime

Base = declarative_base()

class User(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    is_admin = db.Column(db.Boolean, default=False)
    is_checker = db.Column(db.Boolean, default=False)

    is_new_member = db.Column(db.Boolean, default=False)

    personDetail = db.relationship('PersonDetail', backref="user")

    langCompetenceEntries = db.relationship('LangCompetence', backref="user")
    professionalQualificationEntries = db.relationship('ProfessionalQualification', backref="user")
    professionalRecognitionEntries = db.relationship('ProfessionalRecognition', backref="user")
    WorkExperienceEntries = db.relationship('WorkExperience', backref="user")

    #cpdActivityEntries = db.relationship('CpdActivityEntry', backref="user")
    cpdActivityEntryHeaders = db.relationship('CpdActivityEntryHeader', backref="user")

    paymentHistory = db.relationship('PaymentHistory', backref="user")

    UploadData = db.relationship('UploadData', backref="user")

    is_registration_form_submit = db.Column(db.Boolean, default=False)

    random_text_for_password_reset = db.Column(db.String(10))

    def __repr__(self):
        return '<User Email {}>'.format(self.email)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# flask_login
@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class PersonDetail(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(4), nullable=True, default='')
    date_of_birth = db.Column(db.DateTime, nullable=True)
    country_of_birth = db.Column(db.String(10), nullable=True, default='HK')
    
    id = db.Column(db.Integer, primary_key=True)
    name_of_registrant = db.Column(db.String(100))
    chinese_name = db.Column(db.String(50))    
    online_id = db.Column(db.String(50))
    online_registration_date = db.Column(db.DateTime)
    #email = db.Column(db.String(100), index=True, unique=True)
    mobile_phone = db.Column(db.String(50))
    office_phone = db.Column(db.String(50))    
    correspondence_addr = db.Column(db.String(200))
    work_addr = db.Column(db.String(200))

    old_id = db.Column(db.Integer())
   
    is_register = db.Column(db.Boolean, default=False)

    #is_form_submit = db.Column(db.Boolean, default=False)
    #is_form_check = db.Column(db.Boolean, default=False)
    #is_form_approve = db.Column(db.Boolean, default=False)

    date_of_submit =  db.Column(db.DateTime)
    date_of_check =  db.Column(db.DateTime)
    date_of_approve =  db.Column(db.DateTime)

    is_charge_local_annual_fee = db.Column(db.Boolean, default=False)  # Annual amount depends

    #user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Name {}>'.format(self.name_of_registrant)

class LangCompetence(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    #dominant_lang = db.Column(db.String(30))
    _dominant_lang_multiple = db.Column(db.String(100), nullable=False, default='')
    dominant_lang_other = db.Column(db.String(30))

    #lang_training_was_conducted = db.Column(db.String(30))
    _lang_training_was_conducted_multiple = db.Column(db.String(100), nullable=False, default='')
    lang_training_was_conducted_other = db.Column(db.String(30))

    #lang_provide_therapy = db.Column(db.String(30))
    _lang_provide_therapy_multiple = db.Column(db.String(100), nullable=False, default='')
    lang_provide_therapy_other = db.Column(db.String(30))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    @property
    def dominant_lang_multiple(self):
        return [ x for x in self._dominant_lang_multiple.split(';')]

    @dominant_lang_multiple.setter
    def dominant_lang_multiple(self, value):
        self._dominant_lang_multiple = value

    @property
    def lang_training_was_conducted_multiple(self):
        return [ x for x in self._lang_training_was_conducted_multiple.split(';')]

    @lang_training_was_conducted_multiple.setter
    def lang_training_was_conducted_multiple(self, value):
        self._lang_training_was_conducted_multiple = value

    @property
    def lang_provide_therapy_multiple(self):
        return [ x for x in self._lang_provide_therapy_multiple.split(';')]

    @lang_provide_therapy_multiple.setter
    def lang_provide_therapy_multiple(self, value):
        self._lang_provide_therapy_multiple = value

class ProfessionalQualification(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)   
    #qualification_name = db.Column(db.String(200))
    #issue_authority = db.Column(db.String(200))
    issue_year = db.Column(db.String(10))

    qualification_name_in_eng = db.Column(db.String(200))
    issue_authority_in_eng = db.Column(db.String(200))

    country_name = db.Column(db.String(100))
    #language_of_instruction = db.Column(db.String(100))
    #graduation_date =  db.Column(db.DateTime)
    #level = db.Column(db.String(100))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class ProfessionalRecognition(db.Model):

    id = db.Column(db.Integer, primary_key=True)   
    country_name = db.Column(db.String(100))
    organization_name = db.Column(db.String(100))
    membership_type = db.Column(db.String(100))
    expiry_date = db.Column(db.DateTime)

    '''
    upload_file_name = db.Column(db.String(100), default=None, nullable=True)
    upload_file_url = db.Column(db.String(200), default=None, nullable=True)
    '''

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class WorkExperience(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)   
    employer_name = db.Column(db.String(200))
    job_title = db.Column(db.String(100))
    from_date = db.Column(db.DateTime)
    to_date = db.Column(db.DateTime)

    exp_from = db.Column(db.String(10))
    exp_to = db.Column(db.String(10))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Page(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(200), nullable=True)
    title = db.Column(db.String(200), default='', nullable=True)
    #publish_date = db.Column(db.DateTime, default=datetime.datetime.utcnow, nullable=False)
    publish_date = db.Column(db.DateTime, default=datetime.datetime.now, nullable=False)
    content = db.Column(db.Text)
    is_publish = db.Column(db.Boolean, default=False)

class Fee(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    date_effective_to = db.Column(db.DateTime)
    description = db.Column(db.String(200), nullable=False)
    currency =  db.Column(db.String(3), nullable=True, default='HKD')
    amount = db.Column(db.Numeric(10,2), nullable=False)
    type = db.Column(db.String(10), nullable=False) # Local / Overseas

class PaymentHistory(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.datetime.now, nullable=False)
    amount = db.Column(db.Numeric(10,2), nullable=False)
    currency =  db.Column(db.String(3), nullable=True, default='HKD')
    description = db.Column(db.String(200), nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class CpdActivity(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    order_num = db.Column(db.Integer)
    activity_category = db.Column(db.String(300), nullable=False)

    category_description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return '<Activity Category : {}>'.format(self.activity_category)


class CpdActivityEntryHeader(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    start_date =  db.Column(db.DateTime)
    end_date =  db.Column(db.DateTime)
    #approved_date = db.Column(db.DateTime)
    date_of_submit =  db.Column(db.DateTime)

    payment_id = db.Column(db.Integer, db.ForeignKey(PaymentHistory.id))
    payment = db.relationship(PaymentHistory, uselist=False)

    is_closed = db.Column(db.Boolean, default=False)

    is_sent_one_month_before_expiry = db.Column(db.Boolean, default=False)
    is_sent_three_month_grace_period = db.Column(db.Boolean, default=False)
    is_sent_expiry_and_membership_remove = db.Column(db.Boolean, default=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class CpdActivityEntry(db.Model):
#class CpdActivityEntry(Base):

    #__tablename__ = 'cpd_activity_entry'

    id = db.Column(db.Integer, primary_key=True)
    create_date = db.Column(db.DateTime)
    activity_description = db.Column(db.Text)
    point_awarded = db.Column(db.Numeric(3,1), nullable=False)
    #year = db.Column(db.Integer)

    #cpd_activity_id = db.Column(db.Integer, db.ForeignKey('cpd_activity.id'))
    cpd_activity_id = db.Column(db.Integer)
    
    '''
    cpd_activity = db.relationship(
        'CpdActivity',
        backref = db.backref('cpd_activity_entry')
    )
    '''
    
    #cpd_activity = orm.relationship(CpdActivity, backref='cpdActivitiyEntries')

    cpd_activity_entry_header_id = db.Column(db.Integer, db.ForeignKey('cpd_activity_entry_header.id'))

class UploadData(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    create_date = db.Column(db.DateTime)
    filename = db.Column(db.Text)
    uuid_filename = db.Column(db.Text)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class EmailNotice(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    create_date = db.Column(db.DateTime)
    #email = db.Column(db.String(100), index=True, unique=True)
    email = db.Column(db.String(100))

    is_sent_password_reset = db.Column(db.Boolean, default=False)

    is_sent_one_month_before_expiry = db.Column(db.Boolean)
    is_sent_three_month_grace_period = db.Column(db.Boolean)
    is_sent_expiry_and_membership_remove = db.Column(db.Boolean)

    is_sent_check_assessement_form = db.Column(db.Boolean)
    is_sent_approve_assessement_form = db.Column(db.Boolean)

class SystemFunction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    function_name = db.Column(db.String(100))
    is_enabled = db.Column(db.Boolean, default=True)

class CsvData(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name_of_registrant = db.Column(db.String(100))
    chinese_name = db.Column(db.String(50))
    online_id = db.Column(db.String(50))
    online_registration_date = db.Column(db.DateTime)
    email = db.Column(db.String(100), index=True, unique=True)
    
    mobile_phone = db.Column(db.String(50))
    office_phone = db.Column(db.String(50))
    
    correspondence_addr = db.Column(db.String(200))
    work_addr = db.Column(db.String(200))
    
    quali_name_a = db.Column(db.String(200))
    quali_issue_auth_a = db.Column(db.String(200))
    quali_issue_yr_a = db.Column(db.String(10))

    quali_name_b = db.Column(db.String(200))
    quali_issue_auth_b = db.Column(db.String(200))
    quali_issue_yr_b = db.Column(db.String(10))

    quali_name_c = db.Column(db.String(200))
    quali_issue_auth_c = db.Column(db.String(200))
    quali_issue_yr_c = db.Column(db.String(10))
    
    quali_name_d = db.Column(db.String(200))
    quali_issue_auth_d = db.Column(db.String(200))
    quali_issue_yr_d = db.Column(db.String(10))

    exp_post_title_a = db.Column(db.String(200))
    exp_comp_a = db.Column(db.String(200))
    exp_from_a = db.Column(db.String(10))
    exp_to_a = db.Column(db.String(10))

    exp_post_title_b = db.Column(db.String(200))
    exp_comp_b = db.Column(db.String(200))
    exp_from_b = db.Column(db.String(10))
    exp_to_b = db.Column(db.String(10))

    exp_post_title_c = db.Column(db.String(200))
    exp_comp_c = db.Column(db.String(200))
    exp_from_c = db.Column(db.String(10))
    exp_to_c = db.Column(db.String(10))

    exp_post_title_d = db.Column(db.String(200))
    exp_comp_d = db.Column(db.String(200))
    exp_from_d = db.Column(db.String(10))
    exp_to_d = db.Column(db.String(10))

    exp_post_title_e = db.Column(db.String(200))
    exp_comp_e = db.Column(db.String(200))
    exp_from_e = db.Column(db.String(10))
    exp_to_e = db.Column(db.String(10))

    exp_post_title_f = db.Column(db.String(200))
    exp_comp_f = db.Column(db.String(200))
    exp_from_f = db.Column(db.String(10))
    exp_to_f = db.Column(db.String(10))

    exp_post_title_g = db.Column(db.String(200))
    exp_comp_g = db.Column(db.String(200))
    exp_from_g = db.Column(db.String(10))
    exp_to_g = db.Column(db.String(10))

    exp_post_title_h = db.Column(db.String(200))
    exp_comp_h = db.Column(db.String(200))
    exp_from_h = db.Column(db.String(10))
    exp_to_h = db.Column(db.String(10))

    def __repr_(self):
        return '<User {}'.form(self.name_of_registrant)
