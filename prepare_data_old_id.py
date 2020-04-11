from app import app, db
from app.models import CsvData

from app.models import User, PersonDetail, ProfessionalQualification, WorkExperience

csvData_records = CsvData.query.all()

password = app.config['PASSWORD_DEFAULT_VALUE']

for csvData in csvData_records :

    '''
    print(csvData.quali_issue_yr_a)
    print (csvData.quali_name_a)
    print (csvData.quali_issue_auth_a)
    '''

    user = User.query.filter_by(email = csvData.email).first()


    if user is None :
       user = User(email = csvData.email)
       user.set_password(password)
       db.session.add(user)

    else:

        personDetail = PersonDetail.query.filter_by(user_id = user.id).first()
    
        if personDetail :


            #personDetail.online_id = csvData.online_id
            personDetail.old_id = csvData.id

            print(csvData.id)
            print(personDetail.old_id)

    db.session.commit()

