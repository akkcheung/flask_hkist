import uuid
import stripe
import os
import random, string
import time

from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

from flask import render_template, flash, redirect, url_for, request
from flask import current_app
from flask import abort
from flask import send_from_directory, send_file

from flask_admin.contrib.sqla import ModelView
from flask_login import login_user, logout_user, current_user, login_required
#from flask_session import session
from flask_mail import Mail, Message
from flask_paginate import Pagination, get_page_args

from jinja2 import Markup

#from flask_ckeditor import CKEditorField

from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename

from app import app, db, login, uploadSet, admin, mail

from app.forms import LoginForm, SignUpForm, PageForm, PersonDetailForm, LangCompetenceForm, ProfessionalQualificationForm, ProfessionalRecognitionForm, WorkExperienceForm, CpdActivityEntryForm, CpdActivityEntriesForm, UploadForm, ResetPasswordForm, PersonDetailRegisterStatusRefreshForm, ForgetPasswordForm

from app.forms import LangCompetenceEntriesForm, ProfessionalQualificationEntriesForm, ProfessionalRecognitionEntriesForm, WorkExperienceEntriesForm, UploadEntriesForm

from app.models import User, Page, PersonDetail, LangCompetence, ProfessionalQualification, ProfessionalRecognition, WorkExperience, PaymentHistory, Fee, CpdActivity, CpdActivityEntry, CpdActivityEntryHeader, UploadData, EmailNotice 

stripe_keys = {
  'secret_key': app.config['STRIPE_SECRET_KEY'],
  'publishable_key': app.config['STRIPE_PUBLISHABLE_KEY']
}

stripe.api_key = app.config['STRIPE_SECRET_KEY']

def randomString(stringLength):
    """Generate a random string with the combination of lowercase and uppercase letters """

    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(stringLength))


    '''
    @app.route('/run-tasks')
    def run_tasks():
        for i in range(10):
            app.apscheduler.add_job(func=scheduled_task, trigger='date', args=[i], id='j'+str(i))
 
    return 'Scheduled several long running tasks.', 200

    def scheduled_task(task_id):
        for i in range(10):
            time.sleep(1)
            print('Task {} running iteration {}'.format(task_id, i))
    '''

'''
@app.route('/run-tasks')
def run_tasks():
    i=1
    app.apscheduler.add_job(func=scheduled_task, trigger='date', args=[i], id='job'+str(i))

def scheduled_task(task_id):
    #cpdActivityEntryHeader_list = CpdActivityEntryHeader.query.filter_by('is_closed'=None).order_by(id)
    #todo
    cpdActivityEntryHeader_list = CpdActivityEntryHeader.query.order_by('id').all()

    #print('debug')
    #print(cpdActivityEntryHeader_list.count())

    if cpdActivityEntryHeader_list : 
        for cpd_activity_entry_header in cpdActivityEntryHeader_list :

            email_subject=''
            email_template=''

            emailNotice = EmailNotice()
            emailNotice.create_date = datetime.now()

            try:
                if not cpd_activity_entry_header.is_sent_one_month_before_expiry :
                    print('if-1')
                    if not cpd_activity_entry_header.is_sent_three_month_grace_period :  
                        if date.today() + relativedelta(months=1) > cpd_activity_entry_header.end_date.date() :
                            email_subject = "Notice : You have 1 month left to fill your CPD Acitivity form"
                            email_template = 'email_notice_one_month_before_expiry.html' 

                            emailNotice.is_sent_one_month_before_expiry = True

                if not cpd_activity_entry_header.is_sent_three_month_grace_period :  
                    print('if-2')
                    if cpd_activity_entry_header.is_sent_one_month_before_expiry :
                        if cpd_activity_entry_header.end_date.date() > date.today() :
                            email_subject = "Notice : You are provided 3 months grace period to fill your CPD Acitivity form"
                            email_template = 'email_notice_three_months_grace_period.html' 

                            emailNotice.is_sent_three_month_grace_period = True

                if not cpd_activity_entry_header.is_sent_expiry_and_membership_remove :
                    print('if-3')
                    if cpd_activity_entry_header.is_sent_one_month_before_expiry :
                        if cpd_activity_entry_header.is_sent_three_month_grace_period :  
                            #if cpd_activity_entry_header.end_date + relativedelta(months=3) >= datetime.today() :
                            if cpd_activity_entry_header.end_date.date() + relativedelta(months=3) >= date.today() :
                                email_subject = "Notice : Your have reach 3 month graceful period to fill yourCPD Acitivity form and your membership is expired automatically"
                                email_template = 'email_notice_membership_expiry.html' 

                                emailNotice.is_sent_one_month_before_expiry= True

                if emailNotice.is_sent_one_month_before_expiry or emailNotice.is_sent_three_month_grace_period or emailNotice.is_sent_expiry_and_membership_remove :
                    user = User.query.get(cpd_activity_entry_header.user_id)

                    msg = Message(email_subject, sender=app.config['EMAIL_USERNAME'], recipients=[user.email])
                    msg.body = ""
                    msg.html = render_template(email_template)

                    #mail.send(msg)
                    print(">debug:")
                    print("sent email to [" + user.email + "] with subject [" + email_subject + "]")  

                    #emailNotice = EmailNotice(email=user.email)
                    emailNotice.email=user.email
                    db.session.add(emailNotice)

                    db.session.commit()

            except Exception as e:
                print(str(e))
'''


@app.route('/')
@app.route('/index')
def index():
    #return "Hello, World"
    #return render_template('index.html')
    return redirect('/page/news')


@app.route('/login', methods=['GET', 'POST'])
def login():

    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()

    #if form.validate_on_submit():
    if request.method == 'POST' and form.validate():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password', 'warning')
            return redirect(url_for('login'))
        else :
            login_user(user, remember=True)
            flash('login successful', 'info')

        return redirect(url_for('index'))

    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
@login_required
def logout():

    logout_user()
    #return redirect(url_for('index'))
    return redirect('/page/news')


@app.route('/register', methods=['GET', 'POST'])
def register():

    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = SignUpForm()

    #if form.validate_on_submit():
    if request.method == 'POST' and form.validate():
        
        user = User.query.filter_by(email=form.email.data).first()
    
        if user is not None :
            flash('Please use a different email address.', 'warning')

        else :
            #user = User(username=form.username.data, email=form.email.data)
            user = User(email=form.email.data)
            user.set_password(form.password.data)
            user.is_new_member = True            

            db.session.add(user)
            db.session.commit()

            flash('Congratulations, you are now a registered user!', 'success')
            return redirect(url_for('login'))

    return render_template('signup.html', title='Sign Up', form=form)


@app.route('/forget_pwd', methods=['GET', 'POST'])
def forget_pwd():

    form = ForgetPasswordForm()

    if request.method == 'POST' and form.validate():

        #user = User.query.filter_by(email=form.signUp.email.data).first()
        user = User.query.filter_by(email=form.email.data).first()

        if user is None :            
            flash('No such user!', 'warning')

        else :

            #personDetail = PersonDetail.query.filter_by(user_id=user.id).filter_by(date_of_birth=form.askQuestion.answer.data).first()
            #personDetail = PersonDetail.query.filter_by(user_id=user.id).first()

            #if personDetail is None :
            #    flash('No such user !', 'warning')

            #else :
                #user.set_password(form.signUp.password.data)
                #db.session.commit()

            #print('debug')
            #print(randomString(10))

            user.random_text_for_password_reset = randomString(10)
            db.session.commit()

            try:
                msg = Message("Forget Password", sender=app.config['MAIL_USERNAME'], recipients=[user.email])
                msg.body = ""
                msg.html = render_template('email_notice_reset_pwd.html', random_text=user.random_text_for_password_reset, domain_name=app.config['DOMAIN_NAME'])
                mail.send(msg)

                emailNotice = EmailNotice(email=user.email)
                emailNotice.is_sent_password_reset = True
                emailNotice.create_date = datetime.now()
                db.session.add(emailNotice)
                db.session.commit()

                flash('Email is sent!', 'success')

            except Exception as e:
                flash(str(e), 'warning') 

            return redirect(url_for('index'))

    else :        
        print(form.errors)

    return render_template('forget_pwd.html', title='Forget Password', form=form)


@app.route('/reset_pwd/<random_text>', methods=['GET', 'POST'])
#def reset_pwd():
def reset_pwd(random_text):

    form = ResetPasswordForm()
    is_error = False

    if not random_text is None:
        user = User.query.filter_by(random_text_for_password_reset=random_text).first()

    else :
        flash('No Password reset password is process!', 'success')
        return redirect(url_for('login'))
        
    if not user is None : 

        if request.method == 'GET':              
                pass

        if request.method == 'POST' and form.validate():

                user.set_password(form.password.data)
                user.random_text_for_password_reset = ''
                db.session.commit()

                flash('Password is reset!, Please login using new password', 'success')
                return redirect(url_for('login'))

        else :
            print(form.errors)

    else :
        flash('No Password reset is process!', 'warning')
        return redirect(url_for('login'))

    return render_template('reset_pwd.html', title='Reset Password', form=form)


@app.route('/profile', methods=['GET', 'POST'])
def my_profile():

    return render_template('my_profile.html', title='My Profile')    


#@app.route('/payment', methods=['GET'])
@app.route('/member_profile', methods=['GET'])
@login_required
#def payment():
def member_profile():

    personDetail = PersonDetail.query.filter_by(user_id=current_user.id).first() 

    #err_msg = '';

    if not personDetail :
        flash('Please submit your Application first!', 'warning')
        return redirect(url_for('index'))

    if not personDetail.date_of_approve :
        flash('Your Application is not approved yet!', 'warning')
        return redirect(url_for('index'))
        
    last_payment = PaymentHistory.query.filter_by(user_id=current_user.id).order_by(PaymentHistory.date.desc()).first()

    if last_payment: 
        #last_payment_date = last_payment.date.replace(hour=0, minute=0, second=0, microsecond=0)
        next_payment_date = last_payment.date.date() + relativedelta(years=1)
    
    #print('>debug')
    #print(next_payment_date) 
    #print(date.today())


    #is_error = False
    is_outstanding_payment = True
    #if current_user.is_new_member == None or not current_user.is_new_member :

    is_expire = False
    is_suspend = False

    date_of_expire = datetime.now()
    date_of_suspend = datetime.now()

    if last_payment: 
        if  last_payment.date.date() >= date.today() and date.today() < next_payment_date :
            #err_msg = 'Your last payment is made with 12 months!', 'warning'
            #flash('Your last payment is already make within 12 months!', 'warning')
            #return redirect(url_for('index'))
            #is_error = True
            is_outstanding_payment = False

    fee = Fee.query.filter(Fee.date_effective_to > date.today()).filter_by(type='Overseas').first()

    cpdActivityEntryHeader = CpdActivityEntryHeader.query.filter_by(user_id = current_user.id).order_by(CpdActivityEntryHeader.id.desc()).first()

    if cpdActivityEntryHeader : 
        '''
        print('debug')
        print(cpdActivityEntryHeader.id)
        '''

        if cpdActivityEntryHeader.end_date.date() > date.today() : 
            #flash('No annual membership fee is overdue yet!', 'warning')
            #is_error = True
            is_outstanding_payment = False

        if cpdActivityEntryHeader.is_sent_three_month_grace_period :
            is_expire = True
            date_of_expire = cpdActivityEntryHeader.end_date + timedelta(days=1)

        if cpdActivityEntryHeader.is_sent_expiry_and_membership_remove :
            is_suspend = True
            date_of_suspend = cpdActivityEntryHeader.end_date + timedelta(months=3) - timedelat(days=1)

    if personDetail.is_charge_local_annual_fee :
        fee = Fee.query.filter(Fee.date_effective_to > date.today()).filter_by(type='Local').first()        
    else : 
        fee = Fee.query.filter(Fee.date_effective_to > date.today()).filter_by(type='Overseas').first()        

    amount = fee.amount * 100

    page = request.args.get('page', 1, type=int)
    
    payments = PaymentHistory.query.filter_by(user_id=current_user.id).order_by(PaymentHistory.date.desc()).paginate(page, app.config['PAYMENT_HISTORY_RECORD_PER_PAGE'], False)

    #next_url = url_for('payment', page=payments.next_num) \
    next_url = url_for('member_profile', page=payments.next_num) \
        if payments.has_next else None

    #prev_url = url_for('payment', page=payments.prev_num) \
    prev_url = url_for('member_profile', page=payments.prev_num) \
        if payments.has_prev else None

    key = app.config['STRIPE_PUBLISHABLE_KEY']

    #print(err_msg)

    #return render_template('payment.html'
    return render_template('member_profile.html'
        , title='Member\'s Profile' 
        , key = key
        , fee = fee
        , amount = amount
        , payments = payments.items
        , next_url=next_url, prev_url=prev_url
        #, err_msg = err_msg
        #, is_error = is_error
        , is_outstanding_payment = is_outstanding_payment
        , personDetail = personDetail
        , cpdActivityEntryHeader = cpdActivityEntryHeader
        , is_suspend = is_suspend
        , date_of_suspend = date_of_suspend 
        , is_expire = is_expire
        , date_of_expire = date_of_expire 
        )    


@app.route('/charge', methods=['POST'])
@login_required
def charge():

        personDetail = PersonDetail.query.filter_by(user_id = current_user.id).first()

        #last_payment = PaymentHistory.query.filter_by(user_id=current_user.id).order_by("date desc").first()
        last_payment = PaymentHistory.query.filter_by(user_id=current_user.id).order_by(PaymentHistory.date.desc()).first()
       
        try:
            
            charge = stripe.Charge.create(
                #amount=500,
                amount=request.form.get('amount'),
                #currency='usd',
                currency='hkd',
                #description='A Django charge',
                description=request.form.get('description'),
                source=request.form.get('stripeToken')
            )
            
            #p = PaymentHistory(date=datetime.date.today(), amount=request.POST['fee_amount'], currency='HKD', description=request.POST['description'], user=request.user)

            paymentHistory = PaymentHistory()

            #paymentHistory.date = date.today()
            paymentHistory.date = datetime.now()          
            paymentHistory.description = request.form.get('description')
            paymentHistory.currency = 'HKD'
            paymentHistory.amount = request.form.get('fee_amount')
            paymentHistory.user_id = current_user.id
            db.session.add(paymentHistory)

            #personDetail = PersonDetail.query.filter_by(user_id = current_user.id).first()
            if not personDetail.is_register :
                personDetail.is_register = True                                
            
            if current_user.is_new_member :
                current_user.is_new_member = False

            cpdActivityEntryHeader = CpdActivityEntryHeader.query.filter_by(user_id = current_user.id).order_by(CpdActivityEntryHeader.id.desc()).first()

            '''
            if cpdActivityEntryHeader : 
                if cpdActivityEntryHeader.end_date > date.today() :
                    flash('No annual membership fee is overdue yet!', 'warning')
                    return redirect(url_for('payment'))
            '''

            if cpdActivityEntryHeader : 
                cpdActivityEntryHeader.payment_id = paymentHistory.id
                cpdActivityEntryHeader.is_closed = True

            cpdActivityEntryHeader_new = CpdActivityEntryHeader()

            if not cpdActivityEntryHeader : 
                cpdActivityEntryHeader_new.start_date = date.today()
                cpdActivityEntryHeader_new.end_date = date.today() + relativedelta(years=1) - timedelta(days=1)

            else : 
                cpdActivityEntryHeader_new.start_date = cpdActivityEntryHeader.end_date + timedelta(days=1)
                cpdActivityEntryHeader_new.end_date = cpdActivityEntryHeader_new.start_date + relativedelta(years=1) - timedelta(days=1)

            cpdActivityEntryHeader_new.user_id = current_user.id

            db.session.add(cpdActivityEntryHeader_new)
            db.session.commit()

            for i in range(1,10):

                cpdActivityEntry = CpdActivityEntry()
                    
                cpdActivityEntry.cpd_activity_id = i
                #cpdActivityEntry.year = year
                #cpdActivityEntry.user_id = current_user.id
                cpdActivityEntry.point_awarded = 0

                cpdActivityEntry.cpd_activity_entry_header_id = cpdActivityEntryHeader_new.id

                db.session.add(cpdActivityEntry)
                #db.session.commit()

            db.session.commit()

            flash('Thanks for you payment. Your payment is received. Please check your name on the Register of Speech Therapists accredited by Department of Health', 'success')

        except stripe.error.StripeError as e:
            #context['result'] = "<h2>Something goes wrong</h2>"
            print (type(e))
            print (e)

            flash('Something goes wrong. Please contact Administrator!', 'danger')

        except Exception as e:
            #print '%s (%s)' % (e.message, type(e))
            print (type(e))
            print (e)
            # context['result'] = "<h2>Something goes wrong</h2>"
            flash('Something goes wrong. Please contact Administrator!', 'danger')

        #return render(request, 'charge.html')
        #return render(request, 'charge.html', context)
        #return redirect(url_for('payment'))
        return redirect(url_for('member_profile'))


@app.route('/cpd_activities/entry', methods=['GET','POST'])
@app.route('/cpd_activities/<id>', methods=['GET','POST'])
@login_required
#def cpd_activities_entry():
def cpd_activities_entry(id=None):

    today = date.today()
    is_read = False

    cpdActivities = CpdActivity.query.order_by('order_num').all()

    name_of_registrant = ''

    if not current_user.is_admin :
    
        if not id:  
            personDetail = PersonDetail.query.filter_by(user_id = current_user.id).first()

            if personDetail :
                name_of_registrant = personDetail.name_of_registrant

                if not personDetail.date_of_approve:
                    flash("Please complete your Application form first before proceeding !", "warning") 
                    return redirect(url_for('index'))

            if current_user.is_new_member :
                flash("As you are a new member, would you please pay your registration fee before filling CPD !", "warning") 
                return redirect(url_for('index'))
    
    cpdActivityEntryHeader = CpdActivityEntryHeader.query.filter_by(user_id=current_user.id).order_by(CpdActivityEntryHeader.start_date.desc()).first()

    if id:
        if id.isdigit() :
            cpdActivityEntryHeader = CpdActivityEntryHeader.query.filter_by(user_id=current_user.id).filter_by(id=id).first()        
            if current_user.is_admin :
                cpdActivityEntryHeader = CpdActivityEntryHeader.query.filter_by(id=id).first()

    if cpdActivityEntryHeader :
        personDetail = PersonDetail.query.filter_by(user_id = cpdActivityEntryHeader.user_id).first()
        name_of_registrant = personDetail.name_of_registrant

        cpd_activity_entries = CpdActivityEntry.query.filter_by(cpd_activity_entry_header_id=cpdActivityEntryHeader.id).order_by(CpdActivityEntry.cpd_activity_id).all()
    
    else :
        flash('No CPD Activity form is available!', 'warning')
        return redirect(url_for('index'))

    form = CpdActivityEntriesForm()

    if request.method == 'GET':

        for cpd_activity_entry in cpd_activity_entries :

            #cpdActivity = CpdActivity.query.filter_by(id=cpd_activity_entry.cpd_activity_id).first()
            
            loc_data = {
                    "cpd_activity_entry_id" : cpd_activity_entry.id,
                    "activity_description" : cpd_activity_entry.activity_description,
                    "point_awarded" : cpd_activity_entry.point_awarded,
                    "cpd_activity_id" : cpd_activity_entry.cpd_activity_id
                    #"category" : cpdActivity.activity_category,
                    #"category_description" : cpdActivity.category_description
            }

            form.cpd_activity_entries.append_entry(loc_data)

    elif request.method == 'POST' : #and form.validate():

        if form.validate() :
            #pass

            for entry in form.cpd_activity_entries:

                #id = entry.id.data

                cpdActivityEntry = CpdActivityEntry.query.filter_by(id=entry.cpd_activity_entry_id.data).first()
                #cpdActivityEntry = CpdActivityEntry.query.filter_by(id=id).first()

                '''
                print ('>> debug ')
                print(entry.cpd_activity_entry_id.data)
                print(entry.activity_description.data)
                '''

                cpdActivityEntry.activity_description = entry.activity_description.data
                cpdActivityEntry.point_awarded = entry.point_awarded.data

                #db.session.commit()

            #flash('Records are saved!', 'success')
            #return redirect(url_for('index'))

                
            total_points = 0

            for cpd_activity_entry in cpd_activity_entries:
                total_points += cpd_activity_entry.point_awarded

            if request.form.get('button_submit')== 'Save':
                flash('CPD Activity Record Form  is saved!', 'success')
   
            if request.form.get('button_submit') == 'Submit':
                if total_points >= 15 :
                    cpdActivityEntry.date_of_submit = date.today()
                    flash('CPD Activity Record Form is submitted!', 'success')
                    
                else :
                    flash('You have not reach a minimum of 15 CPD-ST points!', 'warning')

            db.session.commit()

            return redirect(url_for('cpd_activities_entry'))

        else :
            #print '%s (%s)' % (e.message, type(e))
            print (form.errors)

    total_points = 0

    for cpd_activity_entry in cpd_activity_entries:
        total_points += cpd_activity_entry.point_awarded

    if cpdActivityEntryHeader.date_of_submit :
        flash('CPD form is already submit!', 'warning')
        is_read = True

    if id:
        if id.isdigit() :
            is_read = True

    '''
    print("debug")
    print(is_read)
    '''

    return render_template('cpd_activities_entry.html', title='CPD Activities Entry', form=form, cpdActivityEntryHeader=cpdActivityEntryHeader, total_points=total_points, is_read=is_read, cpdActivities=cpdActivities, name_of_registrant=name_of_registrant)

@app.route('/cpd_forms/list', methods=['GET'])
@login_required
def cpd_form_list():

    page = request.args.get('page', 1, type=int)
    user_id = current_user.id
    
    if current_user.is_admin :
        user_id = request.args.get('user_id')    
    
    #print("> debug")
    #print(PersonDetail.query.filter_by(is_form_check=False).count())
    #print(user_id)

    cpdActivityEntryHeaders = CpdActivityEntryHeader.query.all()
    #cpdActivityEntryHeaders = CpdActivityEntryHeader.query.filter_by(CpdActivityEntryHeader.user_id=user_id)

    return render_template('cpd_forms_list.html', title='CPD forms List', cpdActivityEntryHeaders=cpdActivityEntryHeaders)


@app.route('/applicants/list', methods=['GET'])
@login_required
def applicant_list():

    if not current_user.is_admin :
        if not  current_user.is_checker :
            abort(404)

    #page = request.args.get('page', 1, type=int)
    page, per_page, offset = get_page_args(page_parameter='page', per_page_parameter='per_page')

    is_approve = request.args.get('is_approve')    

    #print("> debug")
    #print(PersonDetail.query.filter_by(is_form_check=False).count())

    #applicants = PersonDetail.query.filter_by(is_form_check=False).order_by(PersonDetail.name_of_registrant).paginate(page, app.config['MEMBERS_PER_PAGE'], False)
    applicantObjectList = []

    if not is_approve :
        #applicants = PersonDetail.query.order_by(PersonDetail.name_of_registrant).paginate(page, app.config['MEMBERS_PER_PAGE'], False)
        applicants = PersonDetail.query.order_by(PersonDetail.name_of_registrant)
    else :

        if is_approve == 'Y' :
            #applicants = PersonDetail.query.filter(PersonDetail.date_of_approve != None).order_by(PersonDetail.name_of_registrant).paginate(page, app.config['MEMBERS_PER_PAGE'], False)
            applicants = PersonDetail.query.filter(PersonDetail.date_of_approve != None).order_by(PersonDetail.name_of_registrant)

        if is_approve == 'N' :
            #applicants = PersonDetail.query.filter(PersonDetail.date_of_approve == None).order_by(PersonDetail.name_of_registrant).paginate(page, app.config['MEMBERS_PER_PAGE'], False)
            applicants = PersonDetail.query.filter(PersonDetail.date_of_approve == None).order_by(PersonDetail.name_of_registrant)

    for applicant in applicants:

        cpd_activity_entry_header = CpdActivityEntryHeader.query.filter(CpdActivityEntryHeader.user_id == applicant.user_id).filter(CpdActivityEntryHeader.is_closed != True).first();

        cpd_activity_entry_header_id = ''
        valid_period = ''
        
        if cpd_activity_entry_header :
            valid_period = cpd_activity_entry_header.start_date.strftime("%Y/%m/%d") + ' - ' + cpd_activity_entry_header.end_date.strftime("%Y/%m/%d")
            cpd_activity_entry_header_id = cpd_activity_entry_header.id

        applicantObject = { 
            'id' : applicant.id
            , 'name_of_registrant' : applicant.name_of_registrant 
            , 'chinese_name' : applicant.chinese_name
            , 'valid_period' : valid_period
            , 'cpd_activity_entry_header_id' : cpd_activity_entry_header_id
        }

        applicantObjectList.append(applicantObject)

    total = len(applicantObjectList)
    
    #next_url = url_for('applicant_list', page=applicants.next_num) \
    #next_url = url_for('applicant_list', page=applicants.next_num, is_approve=is_approve) \
        #if applicants.has_next else None

    #prev_url = url_for('applicant_list', page=applicants.prev_num) \
    #prev_url = url_for('applicant_list', page=applicants.prev_num, is_approve=is_approve) \
        #if applicants.has_prev else None
    
    #return render_template('applicant_list.html', title='Applicants List', applicants=applicants.items, next_url=next_url, prev_url=prev_url)
    #return render_template('applicant_list.html', title='Applicants List', applicants=applicants.items, next_url=next_url, prev_url=prev_url, is_approve=is_approve)

    pagination_applicants = applicantObjectList[offset: offset + per_page]
    pagination = Pagination(page=page, per_page=per_page, total=total, css_framework='bootstrap4')

    return render_template('applicant_list.html', title='Applicants List', applicants=pagination_applicants, page=page, per_page=per_page, pagination=pagination, is_approve=is_approve)


@app.route('/applicants/search', methods=['POST'])
@login_required
def applicant_search():
    #if form.validate_on_submit():
    #    search = form.search.data

    if request.form.get('is_not_approve') :
        return redirect(url_for('applicant_list', is_approve="N"))

    return redirect(url_for('applicant_list', is_approve="Y"))            


@app.route('/registrants/list', methods=['GET'])
#@app.route('/members/list', methods=['GET', 'POST'])
#@login_required
def member_list():

    page = request.args.get('page', 1, type=int)
    
    #members = PersonDetail.query.filter_by(is_register=True).order_by(PersonDetail.name_of_registrant).all()
    members = PersonDetail.query.filter_by(is_register=True).order_by(PersonDetail.name_of_registrant).paginate(page, app.config['MEMBERS_PER_PAGE'], False)

    next_url = url_for('member_list', page=members.next_num) \
        if members.has_next else None
    prev_url = url_for('member_list', page=members.prev_num) \
        if members.has_prev else None
    
    #return render_template('member_list.html', title='Member List', members=members)
    return render_template('member_list.html', title='Registered Members List', members=members.items, next_url=next_url, prev_url=prev_url)


@app.route('/registrants/status/refresh', methods=['GET', 'POST'])
@login_required
def member_refresh_regisiter_status():

    if not current_user.is_admin :
        abort(404)

    form = PersonDetailRegisterStatusRefreshForm()

    if request.method == 'GET':
        pass

    else :
        members = PersonDetail.query.all()

        date_time_str = str(date.today().year)
        date_time_str = date_time_str + "-01-01 00:00:00"

        date_time_obj = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')

        #app.logger.debug(date_time_obj)

        for member in members :
            
            paymentHistory = PaymentHistory.query.filter_by(user_id=member.user_id).filter(PaymentHistory.date > date_time_obj).first()

            if not paymentHistory is None :
                member.is_register = True

            else :
                member.is_register = False

            db.session.commit()

        flash('Refresh complete!', 'success')
        return redirect(url_for('member_list'))

    return render_template('member_register_status_refresh.html', title='Refresh Members\' register Status', form=form)

@app.route('/page/new', methods=['GET', 'POST'])
@login_required
def page_new():
    form = PageForm()

    if not current_user.is_admin :
            abort(404)

    if request.method == 'POST' and form.validate():
        #page = Page(url=form.url.data)
        page = Page()
        page.url = form.url.data
        page.title = form.title.data
        page.content = form.content.data

        db.session.add(page)
        db.session.commit()

        flash('Page is saved!', 'success')
        return redirect(url_for('index'))

    return render_template('page.html', title='Page', form=form)


@app.route('/page/<page_id>/edit', methods=['GET', 'POST'])
@login_required
def page_edit(page_id):

    form = PageForm()


    if request.method == 'GET':

        if not page_id is None:
            page = Page.query.filter_by(id=page_id).first()
            form = PageForm(obj=page)

    elif request.method == 'POST' and form.validate():
        #page = Page(url=form.url.data)
        #page = Page()        
        page = Page.query.filter_by(id=form.id.data).first()        
        page.url = form.url.data
        page.title = form.title.data
        page.content = form.content.data
        
        db.session.commit()

        flash('Page is saved!', 'success')
        return redirect(url_for('index'))

    return render_template('page.html', title='Page', form=form)


@app.route('/page/<page_id>', methods=['GET'])
#@login_required
def page_show(page_id):
    #pageid = page_id

    if page_id is None:
        abort(404)

    if page_id.isdigit() :
        page = Page.query.filter_by(id=page_id).first()

    else :
        page = Page.query.filter_by(url=page_id).first()

    if page is None:
        abort(404)        

    #current_app.logger.debug(page.title)

    return render_template('page_show.html', title=page.title, page=page)


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
 
    form = UploadForm()

    page = request.args.get('page', 1, type=int)
    
    uploadRecords = UploadData.query.filter_by(user_id=current_user.id).order_by(UploadData.create_date.desc()).paginate(page, app.config['PAYMENT_HISTORY_RECORD_PER_PAGE'], False)

    next_url = url_for('upload', page=uploadRecords.next_num) \
        if uploadRecords.has_next else None

    prev_url = url_for('upload', page=uploadRecords.prev_num) \
        if uploadRecords.has_prev else None


    if request.method == 'GET':
        pass

    elif form.validate_on_submit():
        f = form.photo.data
        #filename = os.fsencode(f.filename)
        filename = f.filename
        filename = filename.encode('utf-8')
        filename = secure_filename(f.filename)
        uuid_filename = str(uuid.uuid4().hex) +  '.' + f.filename.rsplit(".", 1)[1]

        if current_user.is_admin :

            '''
            print(">>debug")
            print(os.path.join(
                os.path.abspath("./"), 'app/static', filename
            ))
            '''

            f.save(os.path.join(
                os.path.abspath("./"), 'app/static', filename
            ))

        else: 

            '''
            print(">>debug")
            print(os.path.join(
                app.instance_path, 'photos', uuid_filename            
            ))
            '''

            f.save(os.path.join(
                app.instance_path, 'photos', uuid_filename            
            ))

        uploadData = UploadData()
        #uploadData.filename = f.filename
        uploadData.filename = filename
        #uploadData.uuid_filename = uuid_filename + '.' + f.filename.rsplit(".", 1)[1]
        uploadData.uuid_filename = uuid_filename
        uploadData.create_date = datetime.now()

        uploadData.user_id = current_user.id

        db.session.add(uploadData)
        db.session.commit()

        flash('File is upload!', 'success')

        #return redirect(url_for('index'))
        return redirect(url_for('upload'))

    else :
        print (form.errors)

    return render_template('upload.html', form=form, title='Upload file(s)', uploadRecords=uploadRecords.items, next_url=next_url, prev_url=prev_url )


#@app.route('/uploads/<path:filename>')
@app.route('/uploads/<id>')
@login_required
def download_file(id):
   
    uploadData = UploadData.query.filter_by(id=id).first()

    #app.logger.debug(uploadData.user_id)
    #app.logger.debug(current_user.id)

    #if uploadData is None or  uploadData.user_id != current_user.id:
    if uploadData is None :
          abort(404)

    else : 
        #if uploadData.user_id != current_user.id or not current_user.is_admin :
        if current_user.is_admin :
            pass

        else : 
            if uploadData.user_id != current_user.id :
                abort(404)

    #return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)
    #return send_from_directory(app.instance_path + '/photos', filename, as_attachment=True)
    return send_file( app.root_path  + '/../instance/photos/' + uploadData.uuid_filename, attachment_filename=uploadData.filename)
    

@app.route('/uploads/<id>/remove')
@login_required
def remove_file(id):
   
    uploadData = UploadData.query.filter_by(id=id).first()

    if uploadData is not None and uploadData.user_id == current_user.id:

        try: 
            if current_user.is_admin :
                os.remove(os.path.abspath("./") + '/app/static/' + uploadData.filename)

            else :
                os.remove(app.instance_path + '/photos/' + uploadData.uuid_filename)

            db.session.delete(uploadData)
            db.session.commit()

        except FileNotFoundError:
            flash('The file doesn\'t not exist!', 'warning')


    from_url = request.args.get('from')

    if from_url is not None:
        return redirect(from_url)

    return redirect(url_for('upload'))
    

@app.errorhandler(404)
def page_not_found(error):
   return render_template('404.html', title = '404'), 404

@app.errorhandler(413)
def request_entity_too_large(error):
   return render_template('413.html', title = '413'), 413


#@app.route('/assessment_form/edit', methods=['GET', 'POST'])
@app.route('/assessment_form/edit', methods=['GET', 'POST'], defaults={'id': None})
@app.route('/assessment_form/<id>/edit', methods=['GET', 'POST'])
@login_required
def assessment_form_edit(id):

    #global current_user_id 
    current_user_id = current_user.id

    #print('>debug')
    #print(id)

    if current_user.is_admin or current_user.is_checker :
        #pass
        personDetail = PersonDetail.query.filter_by(id=id).first()

        #print('>debug')
        #print(personDetail)        

        current_user_id = personDetail.user_id

    else :

        if current_user.is_registration_form_submit :
            flash('Your registration form is submitted already!', 'warning')
            return redirect(url_for('index'))

    p_form = PersonDetailForm(prefix='p-')

    lc_entries_form = LangCompetenceEntriesForm(prefix='lc-')
    pq_entries_form = ProfessionalQualificationEntriesForm(prefix='pq-')
    pr_entries_form = ProfessionalRecognitionEntriesForm(prefix='pr-')
    wk_entries_form = WorkExperienceEntriesForm(prefix='wk-')

    upl_form = UploadForm()
    #upl_b_form = UploadForm(prefix='upb-')
    #upl_c_form = UploadForm(prefix='upc-')

    action = request.args.get('action')

    #uploadRecords = UploadData.query.filter_by(user_id=current_user.id).order_by(UploadData.create_date.desc()).all()
    uploadRecords = UploadData.query.filter_by(user_id=current_user_id).order_by(UploadData.create_date.desc()).all()

    if request.method == 'GET':
        #personDetail = PersonDetail.query.filter_by(user_id=current_user.id).first()
        personDetail = PersonDetail.query.filter_by(user_id=current_user_id).first()
      
        #professionalQualification = ProfessionalQualification.query.filter_by(user_id=current_user.id).first()
        #professionalRecognition = ProfessionalRecognition.query.filter_by(user_id=current_user.id).first()
        
        #workExperience = WorkExperience.query.filter_by(user_id=current_user.id).first()

        if personDetail is None:
            pass
        else :

            p_form = PersonDetailForm(obj=personDetail, prefix='p-')

             
            if personDetail.is_charge_local_annual_fee :
                p_form.local_or_overseas.default = 'local'
            else : 
                p_form.local_or_overseas.default = 'overseas'

            p_form.process(obj=personDetail)
            

        #lc_entries = LangCompetence.query.filter_by(user_id=current_user.id).all()   
        lc_entries = LangCompetence.query.filter_by(user_id=current_user_id).all()   

        #if lc_entries is None:
        if len(lc_entries) == 0:

            #"dominant_lang" : '',
            
            lc_data = {
                "lang_competence_id" : 0,
                
                "dominant_lang_multiple" : '',
                "dominant_lang_other" : '',
                "lang_training_was_conducted_multiple" : '',
                "lang_training_was_conducted_other" : '',
                "lang_provide_therapy_multiple" : '',
                "lang_provide_therapy_other" : '',
            }

            lc_entries_form.lang_competence_entries.append_entry(lc_data)
        
        else :
            
            for lc_entry in lc_entries :
                            
                lc_data = {
                    "lang_competence_id" : lc_entry.id,
                    "dominant_lang_multiple" : lc_entry.dominant_lang_multiple,
                    "dominant_lang_other" : lc_entry.dominant_lang_other,
                    "lang_training_was_conducted_multiple" : lc_entry.lang_training_was_conducted_multiple,
                    "lang_training_was_conducted_other" : lc_entry.lang_training_was_conducted_other,
                    "lang_provide_therapy_multiple" : lc_entry.lang_provide_therapy_multiple,
                    "lang_provide_therapy_other" : lc_entry.lang_provide_therapy_other,
                }

                print(lc_data)

                lc_entries_form.lang_competence_entries.append_entry(lc_data)

        #pq_entries = ProfessionalQualification.query.filter_by(user_id=current_user.id).all()   
        pq_entries = ProfessionalQualification.query.filter_by(user_id=current_user_id).all()   

        #if pq_entries is None:
        if len(pq_entries) == 0:

            pq_data = {
                "professional_qualification_id" : 0,
                #"qualification_name" : '',
                #"issue_authority" : '',
                "issue_year" : '',
                "qualification_name_in_eng" : '',
                "issue_authority_in_eng" : '',
                "country_name" : ''
                #"language_of_instruction" : '',
                #"graduation_date" : '',
                #"level" : ''
            }

            pq_entries_form.professional_qualification_entries.append_entry(pq_data)
        
        else :
            
            for pq in pq_entries :
            
                pq_data = {
                    "professional_qualification_id" : pq.id,
                    #"qualification_name" : pq.qualification_name,
                    #"issue_authority" : pq.issue_authority,
                    "issue_year" : pq.issue_year,
                    "qualification_name_in_eng" : pq.qualification_name_in_eng,
                    "issue_authority_in_eng" : pq.issue_authority_in_eng,
                    "country_name" : pq.country_name
                    #"language_of_instruction" : pq.language_of_instruction,
                    #"graduation_date" : pq.graduation_date,
                    #"level" : pq.level
                }
                
                pq_entries_form.professional_qualification_entries.append_entry(pq_data)

            if action == "add_row_pq" and len(pq_entries_form.professional_qualification_entries) < 3 :

                pq_data = {
                    "professional_qualification_id" : 0,
                    #"qualification_name" : '',
                    #"issue_authority" : '',
                    "issue_year" : '',
                    "qualification_name_in_eng" : '',
                    "issue_authority_in_eng" : '',
                    "country_name" : ''
                    #"language_of_instruction" : '',
                    #"graduation_date" : '',
                    #"level" : ''
                }

                pq_entries_form.professional_qualification_entries.append_entry(pq_data)
            
            elif action == "add_row_pq" :
                flash('Maximun 3 rows are reached!', 'warning')

        #pr_entries = ProfessionalRecognition.query.filter_by(user_id=current_user.id).all()   
        pr_entries = ProfessionalRecognition.query.filter_by(user_id=current_user_id).all()   

        #if pr_entries is None:
        if len(pr_entries) == 0:

            pr_data = {
                "professional_recognition_id" : 0,
                "country_name" : '',
                "organization_name" : '',
                "membership_type" : '',
                "expiry_date" : '',
            }

            pr_entries_form.professional_recognition_entries.append_entry(pr_data)
        
        else :
            
            for pr in pr_entries :
            
                pr_data = {
                    "professional_recognition_id" : pr.id,
                    "country_name" : pr.country_name,
                    "organization_name" : pr.organization_name,
                    "membership_type" : pr.membership_type,
                    "expiry_date" : pr.expiry_date,
                }
                
                pr_entries_form.professional_recognition_entries.append_entry(pr_data)

            if action == "add_row_pr" and len(pr_entries_form.professional_recognition_entries) < 3 :

                pr_data = {
                    "professional_recognition_id" : 0,
                    "country_name" : '',
                    "organization_name" : '',
                    "membership_type" : '',
                    "expiry_date" : '',
                }

                pr_entries_form.professional_recognition_entries.append_entry(pr_data)
            
            elif action == "add_row_pr" :

                flash('Maximun 3 rows are reached!', 'warning')

        #wk_entries = WorkExperience().query.filter_by(user_id=current_user.id).all()
        wk_entries = WorkExperience().query.filter_by(user_id=current_user_id).all()   

        if len(wk_entries) ==0 :

            wk_data = {
                "work_experience_id" : 0,
                "employer_name" : '',
                "job_title" : '',
                "from_date" : '',
                "to_date" : '',
            }

            wk_entries_form.work_experience_entries.append_entry(wk_data)

        else : 

            for wk in wk_entries :
            
                wk_data = {
                    "work_experience_id" : wk.id,
                    "employer_name" : wk.employer_name,
                    "job_title" : wk.job_title,
                    "from_date" : wk.from_date,
                    "to_date" : wk.to_date,
                }
                
                wk_entries_form.work_experience_entries.append_entry(wk_data)

            if action == "add_row_wk" and len(wk_entries_form.work_experience_entries) < 3 :

                wk_data = {
                    "work_experience_id" : 0,
                    "employer_name" : '',
                    "job_title" : '',
                    "from_date" : '',
                    "to_date" : '',
                }

                wk_entries_form.work_experience_entries.append_entry(wk_data)
            
            elif action == "add_row_wk" and len(wk_entries_form.work_experience_entries) == 3 :

                flash('Maximun 3 rows are reached!', 'warning')

        #uploadRecords = UploadData.query.filter_by(user_id=current_user.id).order_by(UploadData.create_date.desc()).all()


    elif request.method == 'POST' and p_form.validate() and lc_entries_form.validate() and pq_entries_form.validate() and pr_entries_form.validate() and wk_entries_form.validate() and upl_form.validate() :
    
        is_error = False

        personDetail = PersonDetail()

        if p_form.id.data:
            #personDetail = PersonDetail.query.filter_by(id=p_form.id.data).first()
            personDetail = PersonDetail.query.get(p_form.id.data)

            if request.form.get('button_submit')== 'Return to applicant for modification':

                #if personDetail.is_form_submit :
                if personDetail.date_of_submit :
                    
                    #personDetail.is_form_check = False
                    #personDetail.is_form_submit = False
                    personDetail.date_of_submit = None
                    personDetail.date_of_check = None
                    
                    user = User.query.get(current_user_id)
                    user.is_registration_form_submit = False

                    #print('>debug')
                    #print(user)

                    db.session.commit()

                    flash('Returned to applicant for modification!', 'success')
                
                else: 
                    flash('Applicant does not submit the application !', 'warning')

                return redirect(url_for('assessment_form_edit', id=p_form.id.data))

            if request.form.get('button_submit')== 'Check Ok':

                if personDetail.date_of_submit and not personDetail.date_of_check :

                    #personDetail.is_form_check = True
                    personDetail.date_of_check = date.today()
                    db.session.commit()

                    flash('Application is checked!', 'success')
                else :

                    if not personDetail.date_of_submit :
                        flash('Applicant does not submit the application !', 'warning')
                    
                    else:
                        flash('Applicant is already checked !', 'warning')

                return redirect(url_for('assessment_form_edit', id=p_form.id.data))

            if request.form.get('button_submit')== 'Approve':

                #if personDetail.is_form_check :
                if personDetail.date_of_check :
                    #personDetail.is_form_approve = True
                    personDetail.date_of_approve = date.today()
                    db.session.commit()

                    #Todo - Send Email


                    flash('Registration is approved!', 'success')

                else :
                    flash('Registration is not checked!', 'warning')

                return redirect(url_for('assessment_form_edit', id=p_form.id.data))

        p_form.populate_obj(personDetail)

        '''
        print('debug')
        print(p_form.local_or_overseas.data)
        '''

        if p_form.local_or_overseas.data == 'local' :
            personDetail.is_charge_local_annual_fee = True

        else : 
            personDetail.is_charge_local_annual_fee = False

        if not p_form.id.data: 
            personDetail.id = None       
            #personDetail.user_id = current_user.id
            personDetail.user_id = current_user_id
            db.session.add(personDetail)

        for form in lc_entries_form.lang_competence_entries :

            #id = entry.id.data

            if int(form.lang_competence_id.data) == 0 :

                langCompetence = LangCompetence()

                langCompetence.id = None

                #langCompetence.dominant_lang = form.dominant_lang.data
                list_of_langs = form.dominant_lang_multiple.data

                langs = "" 
                for ele in list_of_langs:  
                    langs = langs + ele + ";"   

                langCompetence.dominant_lang_multiple = langs
                langCompetence.dominant_lang_other = form.dominant_lang_other.data
                
                #langCompetence.lang_training_was_conducted = form.lang_training_was_conducted.data
                list_of_langs = form.lang_training_was_conducted_multiple.data
                
                langs = "" 
                for ele in list_of_langs:  
                    langs = langs + ele + ";"   

                langCompetence.lang_training_was_conducted_multiple = langs

                langCompetence.lang_training_was_conducted_other = form.lang_training_was_conducted_other.data
                
                #langCompetence.lang_provide_therapy = form.lang_provide_therapy.data
                list_of_langs = form.lang_provide_therapy_multiple.data

                langs = "" 
                for ele in list_of_langs:  
                    langs = langs + ele + ";"   

                langCompetence.lang_provide_therapy_multiple = langs

                langCompetence.lang_provide_therapy_other = form.lang_training_was_conducted_other.data

                #langCompetence.user_id = current_user.id
                langCompetence.user_id = current_user_id

                db.session.add(langCompetence)
                #db.session.commit()
                
            else :

                #langCompetence = LangCompetence.query.filter_by(id=form.lang_competence_id.data).filter_by(user_id=current_user.id).first()
                langCompetence = LangCompetence.query.filter_by(id=form.lang_competence_id.data).filter_by(user_id=current_user_id).first()


                #langCompetence.dominant_lang = form.dominant_lang.data

                list_of_langs = form.dominant_lang_multiple.data

                langs = "" 

                for ele in list_of_langs:  
                    langs = langs + ele + ";"   

                langCompetence.dominant_lang_multiple = langs
                
                langCompetence.dominant_lang_other = form.dominant_lang_other.data

                #langCompetence.lang_training_was_conducted = form.lang_training_was_conducted.data
                
                list_of_langs = form.lang_training_was_conducted_multiple.data

                langs = "" 

                for ele in list_of_langs:  
                    langs = langs + ele + ";"   


                langCompetence.lang_training_was_conducted_multiple = langs
                
                langCompetence.lang_training_was_conducted_other = form.lang_training_was_conducted_other.data
                
                #langCompetence.lang_provide_therapy = form.lang_provide_therapy.data
                list_of_langs = form.lang_provide_therapy_multiple.data

                langs = "" 

                for ele in list_of_langs:  
                    langs = langs + ele + ";"   


                langCompetence.lang_provide_therapy_multiple = langs

                langCompetence.lang_provide_therapy_other = form.lang_provide_therapy_other.data
                
                #db.session.commit()

        for form in pq_entries_form.professional_qualification_entries :

            if int(form.professional_qualification_id.data) == 0 :

                professionalQualification = ProfessionalQualification()

                professionalQualification.id = None

                #professionalQualification.qualification_name = form.qualification_name.data
                #professionalQualification.issue_authority = form.issue_authority.data
                professionalQualification.issue_year = form.issue_year.data
                professionalQualification.qualification_name_in_eng = form.qualification_name_in_eng.data
                professionalQualification.issue_authority_in_eng = form.issue_authority_in_eng.data
                professionalQualification.country_name = form.country_name.data
                #professionalQualification.language_of_instruction = form.language_of_instruction.data
                #professionalQualification.graduation_date = form.graduation_date.data
                #professionalQualification.level = form.level.data

                #professionalQualification.user_id = current_user.id
                professionalQualification.user_id = current_user_id
                
                db.session.add(professionalQualification)
                #db.session.commit()
                
            else :

                #professionalQualification = ProfessionalQualification.query.filter_by(id=form.professional_qualification_id.data).filter_by(user_id=current_user.id).first()
                professionalQualification = ProfessionalQualification.query.filter_by(id=form.professional_qualification_id.data).filter_by(user_id=current_user_id).first()

                #professionalQualification.qualification_name = form.qualification_name.data
                #professionalQualification.issue_authority = form.issue_authority.data
                professionalQualification.issue_year = form.issue_year.data
                professionalQualification.qualification_name_in_eng = form.qualification_name_in_eng.data
                professionalQualification.issue_authority_in_eng = form.issue_authority_in_eng.data
                professionalQualification.country_name = form.country_name.data
                #professionalQualification.language_of_instruction = form.language_of_instruction.data
                #professionalQualification.graduation_date = form.graduation_date.data
                #professionalQualification.level = form.level.data

                #db.session.commit()

        for form in pr_entries_form.professional_recognition_entries :

            if int(form.professional_recognition_id.data) == 0 :

                professionalRecognition = ProfessionalRecognition()

                professionalRecognition.id = None

                professionalRecognition.country_name = form.country_name.data
                professionalRecognition.organization_name = form.organization_name.data
                professionalRecognition.membership_type = form.membership_type.data
                professionalRecognition.expiry_date = form.expiry_date.data

                #professionalRecognition.user_id = current_user.id
                professionalRecognition.user_id = current_user_id
                
                db.session.add(professionalRecognition)
                #db.session.commit()

            else : 

                #professionalRecognition = ProfessionalRecognition.query.filter_by(id=form.professional_recognition_id.data).filter_by(user_id=current_user.id).first()
                professionalRecognition = ProfessionalRecognition.query.filter_by(id=form.professional_recognition_id.data).filter_by(user_id=current_user_id).first()

                professionalRecognition.country_name = form.country_name.data
                professionalRecognition.organization_name = form.organization_name.data
                professionalRecognition.membership_type = form.membership_type.data
                professionalRecognition.expiry_date = form.expiry_date.data

                #db.session.commit()

        for form in wk_entries_form.work_experience_entries :

            if int(form.work_experience_id.data) == 0 :

                workExperience = WorkExperience()

                workExperience.id = None

                workExperience.employer_name = form.employer_name.data
                workExperience.job_title = form.job_title.data
                workExperience.from_date = form.from_date.data
                workExperience.to_date = form.to_date.data    
                #workExperience.user_id = current_user.id
                workExperience.user_id = current_user_id

                db.session.add(workExperience)
                #db.session.commit()

            else : 

                #workExperience = WorkExperience.query.filter_by(id=form.work_experience_id.data).filter_by(user_id=current_user.id).first()
                workExperience = WorkExperience.query.filter_by(id=form.work_experience_id.data).filter_by(user_id=current_user_id).first()

                workExperience.employer_name = form.employer_name.data
                workExperience.job_title = form.job_title.data
                workExperience.from_date = form.from_date.data
                workExperience.to_date = form.to_date.data
 
        if upl_form.validate_on_submit():

            f = upl_form.photo.data

            if f is not None :
                filename = secure_filename(f.filename)

                suffix = f.filename.rsplit(".", 1)[1]

                if suffix not in app.config['ALLOWED_EXTENSIONS'] :
                    flash('File type [' + suffix + '] is not allowed!', 'warning')

                    is_error = True

                else :
                    uuid_filename = str(uuid.uuid4().hex) +  '.' + f.filename.rsplit(".", 1)[1]
                    f.save(os.path.join(
                        app.instance_path, 'photos', uuid_filename            
                    ))

                    uploadData = UploadData()
                    uploadData.filename = f.filename
                    uploadData.uuid_filename = uuid_filename
                    uploadData.create_date = datetime.now()

                    #uploadData.user_id = current_user.id
                    uploadData.user_id = current_user_id

                    db.session.add(uploadData)


        if not is_error :
            
            if request.form.get('button_submit') == 'Submit':

                user = User.query.filter_by(id=current_user.id).first()
                user.is_registration_form_submit = True

                personDetail = PersonDetail.query.filter_by(user_id=current_user.id).first()
                #personDetail.is_form_submit = True
                personDetail.date_of_submit = date.today()

            db.session.commit()

            if request.form.get('button_submit')== 'Save':
                flash('Form is saved!', 'success')
                return redirect(url_for('assessment_form_edit'))

            if request.form.get('button_submit') == 'Submit':
                flash('Form is submitted!', 'success')
                #return redirect(url_for('index'))
                return redirect(url_for('assessment_form_submit_complete'))
            
    else:
        flash('Error occured!', 'danger')        
        #print(wk_form.errors)

        print(lc_entries_form.errors)
        print(pq_entries_form.errors)
        print(pr_entries_form.errors)

    return render_template( 'assessment_form_edit.html'
        , title=''
        , p_form=p_form
        , lc_entries_form = lc_entries_form
        , pq_entries_form = pq_entries_form
        , pr_entries_form = pr_entries_form
        , wk_entries_form = wk_entries_form
        , upl_form = upl_form
        #, upl_b_form = upl_b_form
        #, upl_c_form = upl_c_form
        , uploadRecords=uploadRecords,
        )


@app.route('/assessment_form/submit_complete', methods=['GET', 'POST'])
@login_required
def assessment_form_submit_complete():

    return render_template('assessment_form_submit_complete.html', title = '')


### Flask Admin ###

class AdminModelView(ModelView):
    
    def is_accessible(self):
        if current_user.is_authenticated :
            if current_user.is_admin :
                return True
            return True
        return False

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login', next=request.url))

    can_create = False
    can_edit = False
    can_delete = False  
    page_size = 50  

class AdminModelEditView(AdminModelView):
    #form_overrides = dict(category_description=CKEditorField)
    can_edit = True


class CpdActivityEntryView(AdminModelView):

    column_searchable_list = ['activity_description']  

class PaymentHistoryView(AdminModelView):

    column_searchable_list = ['user.email']   

class PersonDetailView(AdminModelView):

    column_searchable_list = ['name_of_registrant', 'mobile_phone', 'user.email']

class LangCompetenceView(AdminModelView):

    column_searchable_list = ['user.email']   

class ProfessionalQualificationView(AdminModelView):

    column_searchable_list = ['user.email']   

class ProfessionalRecognitionView(AdminModelView):

    column_searchable_list = ['user.email']   

class WorkExperienceView(AdminModelView):

    column_searchable_list = ['user.email']

class UploadDataView(AdminModelView):

    column_exclude_list = ['uuid_filename', ]

    column_searchable_list = ['user.email']
    
    def _filename_formatter(view, context, model, name):
        return Markup(
            u"<a href='%s' target='_blank'>%s</a>" % (
                url_for('download_file', id=model.id),
                model.filename
            )
        ) if model.user else u""

    column_formatters = {
        'filename': _filename_formatter
    }



#admin.add_view(AdminModelView(User, db.session, category="Members Area"))

admin.add_view(PaymentHistoryView(PaymentHistory, db.session, category="Members Area"))

admin.add_view(CpdActivityEntryView(CpdActivityEntry, db.session, category="Members Area"))

admin.add_view(PersonDetailView(PersonDetail, db.session, category="Members Area"))

admin.add_view(LangCompetenceView(LangCompetence, db.session, category="Members Area"))

admin.add_view(ProfessionalQualificationView(ProfessionalQualification, db.session, category="Members Area"))

admin.add_view(ProfessionalRecognitionView(ProfessionalRecognition, db.session, category="Members Area"))

admin.add_view(WorkExperienceView(WorkExperience, db.session, category="Members Area"))

admin.add_view(UploadDataView(UploadData, db.session, category="Members Area"))


admin.add_view(AdminModelEditView(CpdActivity, db.session, category="System Maintenance"))

admin.add_view(AdminModelEditView(Fee, db.session, category="System Maintenance"))

