from app import app, db, mail
from app.models import User, PersonDetail, CpdActivityEntryHeader, EmailNotice

from dateutil.relativedelta import relativedelta
from datetime import date, datetime, timedelta

#from flask_mail import Mail, Message
#from flask import render_template 

from jinja2 import Environment, FileSystemLoader

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

root = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(root, 'app/templates')
env = Environment( loader = FileSystemLoader(templates_dir) )
template = env.get_template('email_notice_common.html')

cpdActivityEntryHeader_list = CpdActivityEntryHeader.query.order_by('id').all()

if cpdActivityEntryHeader_list : 
    for cpd_activity_entry_header in cpdActivityEntryHeader_list :

        email_subject=''
        email_template=''

        #emailNotice = EmailNotice()
        #emailNotice.create_date = datetime.now()

        is_sent_one_month_before_expiry = False ;
        is_sent_three_month_grace_period = False ;
        is_sent_expiry_and_membership_remove = False ;

        print('* * * * *') 
        print(cpd_activity_entry_header.id) 
        print(cpd_activity_entry_header.end_date)

        '''
        print(date.today())
        print(date.today() + relativedelta(months=+1))
        print(date.today() + relativedelta(months=+3))
        '''

        try:
            if not cpd_activity_entry_header.is_closed :
                if not cpd_activity_entry_header.is_sent_one_month_before_expiry :
                    print('if-1')
                    #print(date.today() + relativedelta(month=+1))
                    if date.today() < cpd_activity_entry_header.end_date.date() and date.today() + relativedelta(months=+1) > cpd_activity_entry_header.end_date.date() : 
                        print('if-1-1')
                        is_sent_one_month_before_expiry = True

                if not cpd_activity_entry_header.is_sent_three_month_grace_period :  
                    print('if-2')
                    if date.today() >= cpd_activity_entry_header.end_date.date() and date.today() < cpd_activity_entry_header.end_date.date() + relativedelta(months=+3):
                        print('if-2-1')
                        is_sent_three_month_grace_period = True

                if not cpd_activity_entry_header.is_sent_expiry_and_membership_remove :
                    print('if-3')
                    if date.today() >= cpd_activity_entry_header.end_date.date() + relativedelta(months=+3) :
                        print('if-3-1')
                        is_sent_expiry_and_membership_remove= True

                if is_sent_one_month_before_expiry or is_sent_three_month_grace_period or is_sent_expiry_and_membership_remove :
                    print('if-4')

                    emailNotice = EmailNotice()
                    emailNotice.create_date = datetime.now()

                    personDetail = PersonDetail.query.filter_by(user_id=cpd_activity_entry_header.user_id).first()

                    message = ''

                    if is_sent_one_month_before_expiry :
                        emailNotice.is_sent_one_month_before_expiry = True
                        cpd_activity_entry_header.is_sent_one_month_before_expiry = True

                        email_subject = "Notice : 1 month less to complete your CPD Acitivity record"
                        message = 'Please be remind that you have less than ONE month to complete your CPD record.'

                    if is_sent_three_month_grace_period :
                        emailNotice.is_sent_three_month_grace_period = True
                        cpd_activity_entry_header.is_sent_three_month_grace_period = True

                        email_subject = "Notice : 3 months grace period is provided to complete your CPD record"
                        message = 'Please be remind that you are given THREE months grace period to complete your CPD record.'

                    if is_sent_expiry_and_membership_remove :
                        emailNotice.is_sent_expiry_and_membership_remove= True 
                        cpd_activity_entry_header.is_sent_expiry_and_membership_remove = True
                        personDetail.is_register = False

                        email_subject = "Notice : The expiry date to complete your CPD record is past"  
                        message = 'Please be remind the expiry date to fill your CPD record is past. And your membership is expired accordingly.'

                    user = User.query.get(cpd_activity_entry_header.user_id)
                    print('send to : ' + user.email)

                    mail_server = app.config['MAIL_SERVER'] 

                    msg = MIMEMultipart("alternative")
                    msg["Subject"] = email_subject
                    msg["From"] = app.config['MAIL_USERNAME'] 
                    msg["To"] = user.email

                    part = MIMEText(template.render(message=message), "html")
                    msg.attach(part)

                    if 'gmail' in mail_server :
                        print('use ssl')
                        smtp = smtplib.SMTP_SSL(app.config['MAIL_SERVER'], app.config['MAIL_PORT'])

                        smtp.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
                        smtp.sendmail(app.config['MAIL_USERNAME'], user.email, msg.as_string())

                    else :
                        print('use tls')
                        smtp = smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT'])

                        smtp.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
                        smtp.sendmail(app.config['MAIL_USERNAME'], user.email, msg.as_string())

                    emailNotice.email=user.email

                    db.session.add(emailNotice)
                    db.session.commit()

        except Exception as e:
                print('Fail to send email notice with ' + str(e))


