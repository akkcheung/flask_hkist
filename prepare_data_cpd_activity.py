from app import app, db
#from app.models import CsvData

from app.models import User, PersonDetail, ProfessionalQualification, WorkExperience, CpdActivityEntryHeader, CpdActivityEntry 
from app.models import CsvData

from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta

csvData_records = CsvData.query.all()

#password = app.config['PASSWORD_DEFAULT_VALUE']

for csvData in csvData_records :

    ''' 
    print(csvData.quali_issue_yr_a)
    print (csvData.quali_name_a)
    print (csvData.quali_issue_auth_a)
    '''

    user = User.query.filter_by(email = csvData.email).first()

    if user is None :
        pass
        '''
        user = User(email = csvData.email)
        user.set_password(password)
        db.session.add(user)
        '''
        

    else:

        personDetail = PersonDetail.query.filter_by(user_id = user.id).first()
    
        if personDetail :

            #personDetail.online_id = csvData.online_id
            #personDetail.old_id = csvData.id
            personDetail.date_of_approve = date.today()

            #print(csvData.id)
            #print(personDetail.old_id)

            print(csvData.email)
            print(user.id)

            db.session.commit()
    
            cpdActivityEntryHeader = CpdActivityEntryHeader.query.filter_by(user_id = user.id).order_by(CpdActivityEntryHeader.id.desc()).first()

            '''
            if cpdActivityEntryHeader : 
                if cpdActivityEntryHeader.end_date > date.today() :
                    flash('No annual membership fee is overdue yet!', 'warning')
                    return redirect(url_for('payment'))
            '''

            '''
            if cpdActivityEntryHeader:
                cpdActivityEntryHeader.payment_id = paymentHistory.id
                cpdActivityEntryHeader.is_closed = True

            cpdActivityEntryHeader_new = CpdActivityEntryHeader()
            '''
            

            if not cpdActivityEntryHeader:
                cpdActivityEntryHeader_new = CpdActivityEntryHeader()
                #cpdActivityEntryHeader_new.start_date = date.today()
                cpdActivityEntryHeader_new.start_date = datetime(2020,1,1)
                #cpdActivityEntryHeader_new.end_date = date.today() + relativedelta(years=1) - timedelta(days=1)
                cpdActivityEntryHeader_new.end_date = datetime(2020,1,1) + relativedelta(years=1) - timedelta(days=1)

                cpdActivityEntryHeader_new.user_id = user.id

                db.session.add(cpdActivityEntryHeader_new)
                db.session.commit()

                for i in range(1, 10):

                    cpdActivityEntry = CpdActivityEntry()

                    cpdActivityEntry.cpd_activity_id = i
                    #cpdActivityEntry.year = year
                    #cpdActivityEntry.user_id = current_user.id
                    cpdActivityEntry.point_awarded = 0

                    cpdActivityEntry.cpd_activity_entry_header_id = cpdActivityEntryHeader_new.id

                    db.session.add(cpdActivityEntry)
                    #db.session.commit()

                db.session.commit()
