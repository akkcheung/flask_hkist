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

            personDetail.online_id = csvData.online_id

    '''
        if personDetail is None :

            personDetail = PersonDetail(
                #title = '', 
                #date_of_birth 
                #country_of_birth = 
                name_of_registrant = csvData.name_of_registrant,
                chinese_name = csvData.chinese_name,
                online_registration_date= csvData.online_registration_date,
                mobile_phone = csvData.mobile_phone,
                office_phone = csvData.office_phone,
                correspondence_addr = csvData.correspondence_addr,
                work_addr = csvData.work_addr,
                #is_register

                user_id = user.id
			)

            db.session.add(personDetail)

        professionalQualification = ProfessionalQualification.query.filter_by(user_id = user.id).first()

        if professionalQualification is None :


            print(csvData.quali_issue_yr_a)
            print (csvData.quali_name_a)
            print (csvData.quali_issue_auth_a)
            print (bool(csvData.quali_name_a))

            if bool(csvData.quali_name_a) == True :

                professionalQualification_a = ProfessionalQualification(
                    #qualification_name  =
                    #issue_authority = quali_issue_auth_a
                    issue_year = csvData.quali_issue_yr_a, 

                    qualification_name_in_eng = csvData.quali_name_a,
                    issue_authority_in_eng = csvData.quali_issue_auth_a,

                    #country_name
                    #language_of_instruction
                    #graduation_date
                    #level

                    user_id = user.id
                )            

                db.session.add(professionalQualification_a)
            
            if bool(csvData.quali_name_b) == True :

                professionalQualification_b = ProfessionalQualification(
                    
                    issue_year = csvData.quali_issue_yr_b, 

                    qualification_name_in_eng = csvData.quali_name_b,
                    issue_authority_in_eng = csvData.quali_issue_auth_b,

                    user_id = user.id
                )
                
                db.session.add(professionalQualification_b)

            if bool(csvData.quali_name_c) == True :
            
                professionalQualification_c = ProfessionalQualification(
                    
                    issue_year = csvData.quali_issue_yr_c, 

                    qualification_name_in_eng = csvData.quali_name_c,
                    issue_authority_in_eng = csvData.quali_issue_auth_c,

                    user_id = user.id
                )

                db.session.add(professionalQualification_c)

            if bool(csvData.quali_name_d) == True :
            
                professionalQualification_d = ProfessionalQualification(
                    
                    issue_year = csvData.quali_issue_yr_d, 

                    qualification_name_in_eng = csvData.quali_name_d,
                    issue_authority_in_eng = csvData.quali_issue_auth_d,

                    user_id = user.id
                )

                db.session.add(professionalQualification_d)

        workExperience = WorkExperience().query.filter_by(user_id = user.id).first()

        if workExperience is None :

            print(csvData.exp_comp_a)
            
            if bool(csvData.exp_comp_a) == True :

                workExperience_a = WorkExperience(
                    employer_name = csvData.exp_comp_a,
                    job_title = csvData.exp_post_title_a,
                    exp_from = csvData.exp_from_a,
                    exp_to = csvData.exp_to_a,
                    user_id = user.id
                )

                db.session.add(workExperience_a)

            if bool(csvData.exp_comp_b) == True :

                workExperience_b = WorkExperience(
                    employer_name = csvData.exp_comp_b,
                    job_title = csvData.exp_post_title_b,
                    exp_from = csvData.exp_from_b,
                    exp_to = csvData.exp_to_b,
                    user_id = user.id
                )

                db.session.add(workExperience_b)

            if bool(csvData.exp_comp_c) == True :
            
                workExperience_c = WorkExperience(
                    employer_name = csvData.exp_comp_c,
                    job_title = csvData.exp_post_title_c,
                    exp_from = csvData.exp_from_c,
                    exp_to = csvData.exp_to_c ,
                    user_id = user.id
                )

                db.session.add(workExperience_c)

            if bool(csvData.exp_comp_d) == True :

                workExperience_d = WorkExperience(
                    employer_name = csvData.exp_comp_d,
                    job_title = csvData.exp_post_title_d,
                    exp_from = csvData.exp_from_d,
                    exp_to = csvData.exp_to_d,
                    user_id = user.id
                )

                db.session.add(workExperience_d)
            
            if bool(csvData.exp_comp_e) == True :

                workExperience_e = WorkExperience(
                    employer_name = csvData.exp_comp_e,
                    job_title = csvData.exp_post_title_e,
                    exp_from = csvData.exp_from_e,
                    exp_to = csvData.exp_to_e ,
                    user_id = user.id
                )

              db.session.add(workExperience_e)
    '''

    db.session.commit()
