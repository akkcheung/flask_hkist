from app import app, db

from app.models import User, PersonDetail, ProfessionalQualification, WorkExperience, CpdActivityEntryHeader, CpdActivityEntry 

from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta


personDetails = PersonDetail.query.filter_by(is_register = True).all()

for personDetail in personDetails :

    user = User.query.filter_by(id = personDetail.user_id).first()

    if personDetail.date_of_approve and personDetail.is_register :
        cpdActivityEntryHeader = CpdActivityEntryHeader.query.filter_by(user_id = user.id).order_by(CpdActivityEntryHeader.id.desc()).first()


        if not cpdActivityEntryHeader:
            cpdActivityEntryHeader_new = CpdActivityEntryHeader()
            #cpdActivityEntryHeader_new.start_date = datetime(2020,1,1)
            cpdActivityEntryHeader_new.start_date = personDetail.date_of_approve
            #cpdActivityEntryHeader_new.end_date = datetime(2020,1,1) + relativedelta(years=1) - timedelta(days=1)
            cpdActivityEntryHeader_new.end_date = datetime(2021,12,31)

            cpdActivityEntryHeader_new.user_id = user.id

            db.session.add(cpdActivityEntryHeader_new)
            db.session.commit()

            for i in range(1, 10):

                cpdActivityEntry = CpdActivityEntry()

                cpdActivityEntry.cpd_activity_id = i
                cpdActivityEntry.point_awarded = 0

                cpdActivityEntry.cpd_activity_entry_header_id = cpdActivityEntryHeader_new.id

                db.session.add(cpdActivityEntry)
                db.session.commit()

            print("{email}, user id:{user_id}, cpd header id :{cpd_id}".format(email=user.email, user_id=user.id, cpd_id=cpdActivityEntryHeader_new.id))

