import uuid
import stripe
import os

from datetime import date, datetime

from flask import render_template, flash, redirect, url_for, request
from flask import current_app
from flask import abort
from flask import send_from_directory, send_file

from flask_admin.contrib.sqla import ModelView
from jinja2 import Markup

from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename

from app import app, db, login, uploadSet, admin

from app.forms import LoginForm, SignUpForm, PageForm, PersonDetailForm, LangCompetenceForm, ProfessionalQualificationForm, ProfessionalRecognitionForm, WorkExperienceForm, CpdActivityEntryForm, CpdActivityEntriesForm, UploadForm, ResetPasswordForm, PersonDetailRegisterStatusRefreshForm

from app.forms import LangCompetenceEntriesForm, ProfessionalQualificationEntriesForm, ProfessionalRecognitionEntriesForm, WorkExperienceEntriesForm, UploadEntriesForm

from app.models import User, Page, PersonDetail, LangCompetence, ProfessionalQualification, ProfessionalRecognition, WorkExperience, PaymentHistory, Fee, CpdActivity, CpdActivityEntry, UploadData

stripe_keys = {
  'secret_key': app.config['STRIPE_SECRET_KEY'],
  'publishable_key': app.config['STRIPE_PUBLISHABLE_KEY']
}

stripe.api_key = app.config['STRIPE_SECRET_KEY']

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
            db.session.add(user)
            db.session.commit()

            flash('Congratulations, you are now a registered user!', 'success')
            return redirect(url_for('login'))

    return render_template('signup.html', title='Sign Up', form=form)


@app.route('/reset_pwd', methods=['GET', 'POST'])
def reset_pwd():

    form = ResetPasswordForm()
  
    if request.method == 'POST' and form.validate():

        user = User.query.filter_by(email=form.signUp.email.data).first()

        if user is None :            
            flash('No such user or incorrect Date of Birth!', 'warning')

        else :

            personDetail = PersonDetail.query.filter_by(user_id=user.id).filter_by(date_of_birth=form.askQuestion.answer.data).first()

            if personDetail is None :
                flash('No such user or incorrect Date of Birth!', 'warning')

            else :
                user.set_password(form.signUp.password.data)
                db.session.commit()

                flash('Reset password successful!', 'success')
                return redirect(url_for('login'))

    else :
        print(form.errors)

    return render_template('reset_pwd.html', title='Reset Password', form=form)


@app.route('/profile', methods=['GET', 'POST'])
def my_profile():

    return render_template('my_profile.html', title='My Profile')    


@app.route('/payment', methods=['GET'])
@login_required
def payment():

    fee = Fee.query.filter(Fee.date_effective_to > date.today()).first()

    amount = fee.amount * 100

    page = request.args.get('page', 1, type=int)
    
    payments = PaymentHistory.query.filter_by(user_id=current_user.id).order_by(PaymentHistory.date.desc()).paginate(page, app.config['PAYMENT_HISTORY_RECORD_PER_PAGE'], False)

    next_url = url_for('payment', page=payments.next_num) \
        if payments.has_next else None

    prev_url = url_for('payment', page=payments.prev_num) \
        if payments.has_prev else None

    key = app.config['STRIPE_PUBLISHABLE_KEY']

    return render_template('payment.html'
        , title='Payment' 
        , key = key
        , fee = fee
        , amount = amount
        , payments = payments.items
        , next_url=next_url, prev_url=prev_url
        )    


@app.route('/charge', methods=['POST'])
@login_required
def charge():
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
            db.session.commit()

            #context['result'] = "<h2>Thanks, you paid <strong>$" + request.POST['fee_amount'] + "</strong></h2>"

            flash('Thanks for you payment!', 'success')

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
        return redirect(url_for('payment'))


@app.route('/cpd_activities/entry', methods=['GET','POST'])
@login_required
def cpd_activities_entry():

    #cpd_activitiy_entries = CpdActivityEntry.query.filter_by(user_id=current_user.id).order_by(CpdActivityEntry.cpd_activity_id).all()

    #today = datetime.date.today()
    #year = datetime.date.today().year
    today = date.today()
    year = today.year

    #cpd_activitiy_entries = CpdActivityEntry.query.filter_by(user_id=current_user.id).order_by(CpdActivityEntry.cpd_activity_id).all()

    cpd_activitiy_entries = CpdActivityEntry.query.filter_by(user_id=current_user.id).filter_by(year=year).order_by(CpdActivityEntry.cpd_activity_id).all()

    '''
    print ('>> debug ')
    print ("length is ", len(cpd_activitiy_entries))
    '''
    if len(cpd_activitiy_entries) == 0 :

        for i in range(1,10):

                cpdActivityEntry = CpdActivityEntry()
                
                cpdActivityEntry.cpd_activity_id = i
                cpdActivityEntry.year = year
                cpdActivityEntry.user_id = current_user.id
                cpdActivityEntry.point_awarded = 0

                db.session.add(cpdActivityEntry)
                db.session.commit()

        cpd_activitiy_entries = CpdActivityEntry.query.filter_by(user_id=current_user.id).filter_by(year=year).order_by(CpdActivityEntry.cpd_activity_id).all()

    form = CpdActivityEntriesForm()

    if request.method == 'GET':

        #form = CpdActivityEntriesForm()

        for cpd_activity_entry in cpd_activitiy_entries :

            cpdActivity = CpdActivity.query.filter_by(id=cpd_activity_entry.cpd_activity_id).first()
            
            loc_data = {
                    "cpd_activity_entry_id" : cpd_activity_entry.id,
                    "activity_description" : cpd_activity_entry.activity_description,
                    "point_awarded" : cpd_activity_entry.point_awarded,
                    "cpd_activity_id" : cpd_activity_entry.cpd_activity_id,
                    "category" : cpdActivity.activity_category
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

                db.session.commit()

            flash('Records are saved!', 'success')
            return redirect(url_for('index'))

        else :
            #print '%s (%s)' % (e.message, type(e))
            print (form.errors)


    return render_template('cpd_activities_entry.html', title='CPD Activities Entry', form=form)

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
        filename = secure_filename(f.filename)
        uuid_filename = str(uuid.uuid4().hex) +  '.' + f.filename.rsplit(".", 1)[1]

        f.save(os.path.join(
            app.instance_path, 'photos', uuid_filename            
        ))

        uploadData = UploadData()
        uploadData.filename = f.filename
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

    return render_template('upload.html', form=form, title='upload', uploadRecords=uploadRecords.items, next_url=next_url, prev_url=prev_url )


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
    
    return send_file(app.instance_path + '/photos/' + uploadData.uuid_filename, attachment_filename=uploadData.filename)


@app.route('/uploads/<id>/remove')
@login_required
def remove_file(id):
   
    uploadData = UploadData.query.filter_by(id=id).first()

    if uploadData is not None and uploadData.user_id == current_user.id:

        try: 
            os.remove(app.instance_path + '/photos/' + uploadData.uuid_filename)

        except FileNotFoundError:
            flash('The file doesn\`t not exist!', 'warning')

        db.session.delete(uploadData)
        db.session.commit()

    from_url = request.args.get('from')

    if from_url is not None:
        return redirect(from_url)

    return redirect(url_for('upload'))
    

@app.errorhandler(404)
def page_not_found(error):
   return render_template('404.html', title = '404'), 404


@app.route('/assessment_form/edit', methods=['GET', 'POST'])
@login_required
def assessment_form_edit():

    if current_user.is_registration_form_submit :
        flash('Your registration form is submitted!', 'warning')
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

    uploadRecords = UploadData.query.filter_by(user_id=current_user.id).order_by(UploadData.create_date.desc()).all()

    if request.method == 'GET':
        personDetail = PersonDetail.query.filter_by(user_id=current_user.id).first()
      
        #professionalQualification = ProfessionalQualification.query.filter_by(user_id=current_user.id).first()
        #professionalRecognition = ProfessionalRecognition.query.filter_by(user_id=current_user.id).first()
        
        #workExperience = WorkExperience.query.filter_by(user_id=current_user.id).first()

        if personDetail is None:
            pass
        else :
            p_form = PersonDetailForm(obj=personDetail, prefix='p-')
      
        lc_entries = LangCompetence.query.filter_by(user_id=current_user.id).all()   

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

        pq_entries = ProfessionalQualification.query.filter_by(user_id=current_user.id).all()   

        #if pq_entries is None:
        if len(pq_entries) == 0:

            pq_data = {
                "professional_qualification_id" : 0,
                "qualification_name" : '',
                "issue_authority" : '',
                "issue_year" : '',
                "qualification_name_in_eng" : '',
                "issue_authority_in_eng" : '',
                "country_name" : '',
                "language_of_instruction" : '',
                "graduation_date" : '',
                "level" : ''
            }

            pq_entries_form.professional_qualification_entries.append_entry(pq_data)
        
        else :
            
            for pq in pq_entries :
            
                pq_data = {
                    "professional_qualification_id" : pq.id,
                    "qualification_name" : pq.qualification_name,
                    "issue_authority" : pq.issue_authority,
                    "issue_year" : pq.issue_year,
                    "qualification_name_in_eng" : pq.qualification_name_in_eng,
                    "issue_authority_in_eng" : pq.issue_authority_in_eng,
                    "country_name" : pq.country_name,
                    "language_of_instruction" : pq.language_of_instruction,
                    "graduation_date" : pq.graduation_date,
                    "level" : pq.level
                }
                
                pq_entries_form.professional_qualification_entries.append_entry(pq_data)

            if action == "add_row_pq" and len(pq_entries_form.professional_qualification_entries) < 3 :

                pq_data = {
                    "professional_qualification_id" : 0,
                    "qualification_name" : '',
                    "issue_authority" : '',
                    "issue_year" : '',
                    "qualification_name_in_eng" : '',
                    "issue_authority_in_eng" : '',
                    "country_name" : '',
                    "language_of_instruction" : '',
                    "graduation_date" : '',
                    "level" : ''
                }

                pq_entries_form.professional_qualification_entries.append_entry(pq_data)
            
            elif action == "add_row_pq" :
                flash('Maximun 3 rows are reached!', 'warning')

        pr_entries = ProfessionalRecognition.query.filter_by(user_id=current_user.id).all()   

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

        wk_entries = WorkExperience().query.filter_by(user_id=current_user.id).all()   

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

        p_form.populate_obj(personDetail)

        if not p_form.id.data: 
            personDetail.id = None       
            personDetail.user_id = current_user.id
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
                langCompetence.lang_training_was_conducted = form.lang_training_was_conducted.data
                langCompetence.lang_training_was_conducted_other = form.lang_training_was_conducted_other.data
                langCompetence.lang_provide_therapy = form.lang_provide_therapy.data
                langCompetence.lang_provide_therapy_other = form.lang_training_was_conducted_other.data

                langCompetence.user_id = current_user.id

                db.session.add(langCompetence)
                #db.session.commit()
                
            else :

                langCompetence = LangCompetence.query.filter_by(id=form.lang_competence_id.data).filter_by(user_id=current_user.id).first()

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

                professionalQualification.qualification_name = form.qualification_name.data
                professionalQualification.issue_authority = form.issue_authority.data
                professionalQualification.issue_year = form.issue_year.data
                professionalQualification.qualification_name_in_eng = form.qualification_name_in_eng.data
                professionalQualification.issue_authority_in_eng = form.issue_authority_in_eng.data
                professionalQualification.country_name = form.country_name.data
                professionalQualification.language_of_instruction = form.language_of_instruction.data
                professionalQualification.graduation_date = form.graduation_date.data
                #professionalQualification.level = form.level.data

                professionalQualification.user_id = current_user.id
                
                db.session.add(professionalQualification)
                #db.session.commit()
                
            else :

                professionalQualification = ProfessionalQualification.query.filter_by(id=form.professional_qualification_id.data).filter_by(user_id=current_user.id).first()

                professionalQualification.qualification_name = form.qualification_name.data
                professionalQualification.issue_authority = form.issue_authority.data
                professionalQualification.issue_year = form.issue_year.data
                professionalQualification.qualification_name_in_eng = form.qualification_name_in_eng.data
                professionalQualification.issue_authority_in_eng = form.issue_authority_in_eng.data
                professionalQualification.country_name = form.country_name.data
                professionalQualification.language_of_instruction = form.language_of_instruction.data
                professionalQualification.graduation_date = form.graduation_date.data
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

                professionalRecognition.user_id = current_user.id
                
                db.session.add(professionalRecognition)
                #db.session.commit()

            else : 

                professionalRecognition = ProfessionalRecognition.query.filter_by(id=form.professional_recognition_id.data).filter_by(user_id=current_user.id).first()

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
                workExperience.user_id = current_user.id

                db.session.add(workExperience)
                #db.session.commit()

            else : 

                workExperience = WorkExperience.query.filter_by(id=form.work_experience_id.data).filter_by(user_id=current_user.id).first()

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

                    uploadData.user_id = current_user.id

                    db.session.add(uploadData)


        if not is_error :
            
            if request.form.get('button_submit') == 'Submit':

                user = User.query.filter_by(id=current_user.id).first()
                user.is_registration_form_submit = True                

            db.session.commit()


            if request.form.get('button_submit')== 'Save':
                flash('Form is saved!', 'success')
                return redirect(url_for('assessment_form_edit'))

            if request.form.get('button_submit') == 'Submit':
                flash('Form is submitted!', 'success')
                return redirect(url_for('index'))
            
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
   
    can_edit = True

class CpdActivityEntryView(AdminModelView):

    column_searchable_list = ['user.email']  

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

