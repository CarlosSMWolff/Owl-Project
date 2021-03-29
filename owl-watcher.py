import smtplib
import time
import imaplib
import email
import traceback 
import re
import datetime
import pandas as pd
import numpy as np
from functionsItalki import *
from functionscafetalk_v2 import *
from functions_mail_v2 import *
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
print("=================================================")
print("\nStarting Project Owl at ")
print(datetime.datetime.now()) 



ORG_EMAIL   = "@gmail.com"
FROM_EMAIL  = "carmen.doncel.arauzo" + ORG_EMAIL
#FROM_PWD    = "psjussvqdfdkegbm" # Carlos
#FROM_PWD    = "getsiqquukyrjgxh" # Carmen
#FROM_PWD    = "ugnmitusviccrqkp" # OWL-UAM Linux (project.owl.watcher@gmail.com)
FROM_PWD = "hvxuayokuxvtpywv" #Carmen from Raspberry-Pi
SMTP_SERVER = "imap.gmail.com"
SMTP_PORT   = 993

mail = imaplib.IMAP4_SSL(SMTP_SERVER);
mail.login(FROM_EMAIL,FROM_PWD);
mail.select('inbox');

print("Reading CafeTalk emails")
#######################################################
# FIRST PART:  Find emails from CafeTalk
dataCT = mail.search(None,'SUBJECT "new lesson request" FROM "no-reply@cafetalk.com"')
mail_ids = dataCT[1]
id_list1 = mail_ids[0].split()
dataCT = mail.search(None,'SUBJECT "Reschedule Request" FROM "no-reply@cafetalk.com"')
mail_ids = dataCT[1]
id_list2 = mail_ids[0].split()
id_list=id_list1+id_list2
int_id_list = sorted([int(x) for x in id_list])

N = 15 # Number of LAST cafetalk emails to fetch
n_messages = len(id_list)


savefilename=dir_path+'/Requested-Lessons/CT-lessons-requested.csv'
dfOld=pd.read_csv(savefilename)
# Look for NEW, UNPROCESSED REQUESTS
oldIDlist = dfOld["Id"].tolist()

# Look at all emails from Cafetalk
CT_mails_data = []
for idx in range(n_messages-1,n_messages-N-1,-1):
    id_mail = int(id_list[idx])
    Subject, From, body = mail_reader(mail,id_mail)
    CT_mails_data.append(request_info_CT(body,dfOld))
    
column_names = ["Name","StartDate","EndDate","Duration","Id"]
dfNew = pd.DataFrame(CT_mails_data, columns=column_names)



dfOldNew = dfOld.copy()
for idx in range(N):
    lessondf = dfNew.loc[idx] # I use this weird format so it remains a df
    newFlag = lessondf.Id in oldIDlist
    
    # ACTION if new email found!!!
    if newFlag==False:
        print("\nNew instance found for Cafetalk: we will update the registers")
        dfOldNew=pd.concat([dfNew.loc[idx:idx],dfOldNew],ignore_index=True)
        year = lessondf['StartDate'].year
        month_desired = lessondf['StartDate'].month
        day_desired = lessondf['StartDate'].day
        hour_req_ini = lessondf['StartDate'].hour
        min_req_ini = lessondf['StartDate'].minute
        hour_req_fin = lessondf['EndDate'].hour
        min_req_fin = lessondf['EndDate'].minute
        lesson_id = str(lessondf.Id)     
        
        today = datetime.date.today()
        date_class = datetime.date(year,month_desired,day_desired)

        # Check if its a proper class (not homework)
        if (lessondf.Duration >0) and (date_class>=today):
            print("\nAction necessary: we must modify calendar in Italki")
 
             
            print("\nLesson ID is :"+lesson_id)     
            try:
                statusItalki, before_ss, after_ss = ModifyCalendarItalki(month_desired,day_desired,hour_req_ini,min_req_ini,hour_req_fin,min_req_fin,lesson_id)
            except:
                statusItalki = -2 # Signals an except from resultItalki
                before_ss = dir_path+"/Screenshots/error-robot.jpg"
                after_ss = dir_path+"/Screenshots/error-robot.jpg"           
            print("\nStatus of operation: "+str(statusItalki))
            time_lesson=str(hour_req_ini).zfill(2)+":"+str(min_req_ini).zfill(2)
            date_lesson = str(day_desired)+"/"+str(month_desired)+"/"+str(year)
            student_name = lessondf.Name
            duration = str(int(lessondf.Duration))
            
            # Manda el email informativo!
            send_mail_calendar_change("Italki",student_name,statusItalki,\
            date_lesson,time_lesson,duration,before_ss,after_ss)
            
            dfOldNew.to_csv(savefilename,index=False)
            	
            time.sleep(1) # Give it a rest
        # If its homework class, just update the register
        else:
            dfOldNew.to_csv(savefilename,index=False)
#print("Updating Cafetalk request database")               	


#######################################################
# SECOND PART: Find emails from Italki
# Two types of mails
'''
print("Reading Italki new lessons")
dataIT = mail.search(None,'SUBJECT request FROM "noreply@italki.com"')
mail_ids = dataIT[1]
id_list1 = mail_ids[0].split()
# This catches trial lessons
dataIT = mail.search(None,'SUBJECT "requested a Trial" FROM "noreply@italki.com"')
mail_ids = dataIT[1]
id_list2 = mail_ids[0].split()
id_list=sorted(id_list1+id_list2)

N = min(15,len(id_list)) # Number of LAST italki emails to fetch
n_messages = len(id_list)
'''
# ===========================================
# Enter Italki and check new lessons!

savefilename=dir_path+'/Requested-Lessons/IT-lessons-requested.csv'
dfOldIT=pd.read_csv(savefilename)

dfNewIT = request_info_IT_web(dfOldIT)

# Look for NEW, UNPROCESSED REQUESTS
oldIDlist = dfOldIT["Id"].tolist()
dfOldNew = dfOldIT.copy()






if not (isinstance(dfNewIT, int)):
# If our result did NOT return an int (-1), then we must have new classes detected, run the usual thing
    print("We found new classes in Italki: let us check if they are in the database")
    for idx in range(len(dfNewIT)):
        lessondf = dfNewIT.loc[idx] 
        newFlag = lessondf.Id in oldIDlist
        # ACTION if new email found!!!
        # MODIFY CALENDAR IN CAFETALK!!!
        if newFlag==False:
            print("\nNew instance found for Italki: we will update the registers")
            dfOldNew=pd.concat([dfNewIT.loc[idx:idx],dfOldNew],ignore_index=True)
        
            year = lessondf['StartDate'].year
            month_desired = lessondf['StartDate'].month
            day_desired = lessondf['StartDate'].day
            hour_req_ini = lessondf['StartDate'].hour
            min_req_ini = lessondf['StartDate'].minute
            hour_req_fin = lessondf['EndDate'].hour
            min_req_fin = lessondf['EndDate'].minute
            lesson_id = str(lessondf.Id)
            
            today = datetime.date.today()
            date_class = datetime.date(year,month_desired,day_desired)

            # Check if its a proper class (not homework)
            if (lessondf.Duration >0) and (date_class>=today):
                print("\nAction necessary: we must modify calendar in Cafetalk")

                print("\nLesson ID is :"+lesson_id)
                
                try:
                    statusCafetalk, before_ss, after_ss = ModifyCalendarCafeTalk(month_desired,day_desired,hour_req_ini,min_req_ini,hour_req_fin,min_req_fin,year,lesson_id)
                except:
                    statusCafetalk = -2
                    before_ss = dir_path+"/Screenshots/error-robot.jpg"
                    after_ss = dir_path+"/Screenshots/error-robot.jpg"
                    
                print("\nStatus of operation: "+str(statusCafetalk))
                
                time_lesson=str(hour_req_ini).zfill(2)\
              +":"+str(min_req_ini).zfill(2)
                date_lesson = str(day_desired)+"/"+str(month_desired)+"/"+str(year)
                student_name = lessondf.Name
                duration = str(int(lessondf.Duration))
                
                # Manda el email informativo!
                send_mail_calendar_change("CafeTalk",student_name,statusCafetalk,\
                date_lesson,time_lesson,duration,before_ss,after_ss)
                
                # I update the register INSIDE the loop. This way, if a new Owl-watcher is launched while this is still operating, the new will see the update
                dfOldNew.to_csv(savefilename,index=False)
                
                time.sleep(1) # Give it a rest
                    
            # If its homework class, just update the register
            else:
                dfOldNew.to_csv(savefilename,index=False)

#print("Updating Italki request database")        


print("\nClosing Project Owl at ") 
print(datetime.datetime.now())
