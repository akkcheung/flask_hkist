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

                if not cpd_activity_entry_header.is_sent_three_month_before_expiry :
                    print('if-A')
                    if date.today() < cpd_activity_entry_header.end_date.date() and date.today() + relativedelta(months=+3) > cpd_activity_entry_header.end_date.date() : 
                        print('if-A-1')
                        is_sent_three_month_before_expiry = True

                if not cpd_activity_entry_header.is_sent_one_month_before_expiry :
                    print('if-B')
                    #print(date.today() + relativedelta(month=+1))
                    if date.today() < cpd_activity_entry_header.end_date.date() and date.today() + relativedelta(months=+1) > cpd_activity_entry_header.end_date.date() : 
                        print('if-B-1')
                        is_sent_one_month_before_expiry = True

                if not cpd_activity_entry_header.is_sent_three_month_grace_period :  
                    print('if-C')
                    if date.today() >= cpd_activity_entry_header.end_date.date() and date.today() < cpd_activity_entry_header.end_date.date() + relativedelta(months=+3):
                        print('if-C-1')
                        is_sent_three_month_grace_period = True

                if not cpd_activity_entry_header.is_sent_expiry_and_membership_remove :
                    print('if-D')
                    if date.today() >= cpd_activity_entry_header.end_date.date() + relativedelta(months=+3) :
                        print('if-D-1')
                        is_sent_expiry_and_membership_remove= True

                if is_sent_three_month_grace_period or is_sent_one_month_before_expiry or is_sent_three_month_grace_period or is_sent_expiry_and_membership_remove :
                    print('if-E')

                    emailNotice = EmailNotice()
                    emailNotice.create_date = datetime.now()

                    personDetail = PersonDetail.query.filter_by(user_id=cpd_activity_entry_header.user_id).first()

                    message = ''

                    if is_sent_three_month_before_expiry :
                        emailNotice.is_sent_three_month_before_expiry = True
                        cpd_activity_entry_header.is_sent_three_month_before_expiry = True

                        email_subject = 'Membership Renewal'
                        message = 'Speech Therapists are encouraged to commit to life-long learning to ensure their knowledge and skills are up-to-date in order to deliver the highest level of care to their clients and stakeholders. Registrants of Hong Kong Institute of Speech Therapists Limited (HKIST) must engage in a range of activities to meet a minimum number of Continuous Professional Development for Speech Therapists (CPD-ST) points in order to renew their annual membership of HKIST. Any CPD-ST point earned during the membership renewal period should be immediately submitted in the online CPD Log system. Speech Therapists must accumulate a minimum of 15 CPD-ST points per year to be eligible to renew their HKIST membership. The membership renewal commences from one month before the annual membership expired and this is a warm reminder for you to input all your CPD-ST points earned this year. Members with inadequate CPD-ST points are not eligible for membership renewal. <p></p>For details, please refer to The Continuing Professional Development Framework of HKIST which can be downloaded from our website, www.hkist.org.hk.'

                    if is_sent_one_month_before_expiry :
                        emailNotice.is_sent_one_month_before_expiry = True
                        cpd_activity_entry_header.is_sent_one_month_before_expiry = True

                        email_subject = 'Membership Renewal'
                        message = 'Thank you for your registration in HKIST. The membership renewal commences from one month before the annual membership expired and this is a warm reminder for you to log in to HKIST\'s webpage (www.hkist.org.hk) and start the renewal process.'

                    if is_sent_three_month_grace_period :
                        emailNotice.is_sent_three_month_grace_period = True
                        cpd_activity_entry_header.is_sent_three_month_grace_period = True

                        email_subject = "Membership Renewal"
                        message = "Speech Therapists must accumulate a minimum of 15 CPD-ST points per year, carry an updated professional insurance cover and submit a membership fee of HKD 1500 to be eligible to renew their HKIST membership. A 3-month period will be allowed for members to fulfill the above-mentioned requirements for their annual membership renewal. If the member fails to meet the requirements within this period, he/she will no longer be eligible for their HKIST full membership. The membership will be considered to be lapsed and such individual will be required to re-apply for HKIST full membership. <p></p>According to our system record, you have not reached all of the requirements. This is an email notification for you to engage in sufficient CPD activities, renew your professional insurance cover and submit the membership fee within this 3-month period so that you can proceed with your membership renewal. <p></p>For details, please refer to The Continuing Professional Development Framework of HKIST which can be downloaded from our website, www.hkist.org.hk.'"

                    if is_sent_expiry_and_membership_remove :
                        emailNotice.is_sent_expiry_and_membership_remove= True 
                        cpd_activity_entry_header.is_sent_expiry_and_membership_remove = True
                        personDetail.is_register = False

                        email_subject = "Suspension of Membership"
                        message = "Speech Therapists must accumulate a minimum of 15 CPD-ST points per year, carry an updated professional insurance cover and submit a membership fee of HKD 1500 or HKD 3000(Overseas) to be eligible to renew their HKIST membership. A 3-month period will be allowed for members to fulfill the above-mentioned requirements for their annual membership renewal. <p></p>According to our system record, you have not reached all of the requirements. An email notification was sent to you with a 3-month grace period. However, we did not receive any update from you, regrettably we have to notice you that you are no longer be eligible for their HKIST full membership. The membership will be considered to be lapsed and you will be required to re-apply for HKIST full membership.<p></p>For details, please refer to The Continuing Professional Development Framework of HKIST which can be downloaded from our website, www.hkist.org.hk.'"

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


