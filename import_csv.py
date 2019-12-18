import csv
#from numpy import genfromtxt
#import pandas as pd
import datetime

from app import db
from app.models import CsvData
'''
def Load_Data(file_name):
    data = genfromtxt(file_name, delimiter=',', skiprows=5, converters={0: lambda s: str(s)})
    return data.tolist()
'''

def convert_date(date_str):
	format_str = '%d/%m/%Y'
	datetime_obj = datetime.datetime.strptime(date_str, format_str)
	return datetime_obj.date()


with open('HKIST_Database_csv.csv', newline='') as csvfile:
	readCSV = csv.reader(csvfile, delimiter=',', quotechar='"')

	i=1
	for row in readCSV:
		#print('|'.join(row))
		if i > 5:
			print(row[0])
			print(row[1])
		
			data = CsvData(
				id=row[0], 
				name_of_registrant=row[1], 
				chinese_name = row[2],
				online_id = row[3],
				online_registration_date = convert_date(row[4]),
				email = row[5],

				mobile_phone = row[6],
				office_phone = row[7],

				correspondence_addr = row[8],
				work_addr = row[9],

				quali_name_a = row[10],
				quali_issue_auth_a = row[11],
				quali_issue_yr_a = row[12],
				
				quali_name_b = row[13],
				quali_issue_auth_b = row[14],
				quali_issue_yr_b = row[15],

				quali_name_c = row[16],
				quali_issue_auth_c = row[17],
				quali_issue_yr_c = row[18],

				quali_name_d = row[19],
				quali_issue_auth_d = row[20],
				quali_issue_yr_d = row[21],

				exp_post_title_a = row[22],
				exp_comp_a = row[23], 
				exp_from_a = row[24],
				exp_to_a = row[25],

				exp_post_title_b = row[26],
				exp_comp_b = row[27], 
				exp_from_b = row[28],
				exp_to_b = row[29],

				exp_post_title_c = row[30],
				exp_comp_c = row[31], 
				exp_from_c = row[32],
				exp_to_c = row[33],

				exp_post_title_d = row[34],
				exp_comp_d = row[35], 
				exp_from_d = row[36],
				exp_to_d = row[37],

				exp_post_title_e = row[38],
				exp_comp_e = row[39], 
				exp_from_e = row[40],
				exp_to_e = row[41],

				exp_post_title_f = row[42],
				exp_comp_f = row[43], 
				exp_from_f = row[44],
				exp_to_f = row[45],

				exp_post_title_g = row[46],
				exp_comp_g = row[47], 
				exp_from_g = row[48],
				exp_to_g = row[49],

				exp_post_title_h = row[50],
				exp_comp_h = row[51], 
				exp_from_h = row[52],
				exp_to_h = row[53]
			)
			
			db.session.add(data)
			db.session.commit()

		i= i+ 1

		