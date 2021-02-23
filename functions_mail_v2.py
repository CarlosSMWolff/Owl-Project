import smtplib
import time
import imaplib
import email
import traceback 
import re
import datetime
import pandas as pd
import numpy as np
import os


from email.header import decode_header


# Copied from https://www.thepythoncode.com/article/reading-emails-in-python

def mail_reader(mail,id_mail):
    
    res, msg = mail.fetch(str(id_mail), "(RFC822)")
    for response in msg:
        if isinstance(response, tuple):
            # parse a bytes email into a message object
            msg = email.message_from_bytes(response[1])
            # decode the email subject
            subject, encoding = decode_header(msg["Subject"])[0]
            if isinstance(subject, bytes):
                # if it's a bytes, decode to str
                subject = subject.decode(encoding)
            # decode email sender
            From, encoding = decode_header(msg.get("From"))[0]
            if isinstance(From, bytes):
                From = From.decode(encoding)

            # if the email message is multipart
            if msg.is_multipart():
                # iterate over email parts
                for part in msg.walk():
                    # extract content type of email
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    try:
                        # get the email body
                        body = part.get_payload(decode=True).decode()
                    except:
                        pass

            else:
                # extract content type of email
                content_type = msg.get_content_type()
                # get the email body
                body = msg.get_payload(decode=True).decode()
                
    return subject, From, body

def request_info_CT(body,dfOld):
    
    if("Reschedule requested") in body:
        student_name = re.search('Student Name:(.*)\r',body).group(1)
        date_req=re.search('First Choice: (.*)\r',body).group(1)
        date_req_splt = date_req.split()
        time = date_req_splt[2]
        year = date_req_splt[0].split("/")[0]
        day = date_req_splt[0].split("/")[2]
        month_str = date_req_splt[0].split("/")[1]
        date_req_str = " ".join([month_str,day,year,time])

        dateStart = datetime.datetime.strptime(date_req_str, '%m %d %Y %H:%M')
        
        
        request_id=int(re.search('id=(.*)&',body).group(1))

        # ==== Find if this is really a new request===
        # Get list of previous IDs without any extension
        id_pre_basic=[str(x)[:7] for x in dfOld.Id.tolist()]
        # Find how many previous request exist like this one
        nprev=sum([int((request_id)==x) for x in id_pre_basic])
        if nprev>1:
            # This reschedule might be already captured, and I should not upgrade the Id
            mask_prev=[(id_pre_basic[1])==x for x in id_pre_basic]
            dfPrev=dfOld[mask_prev]
            matches=[]
            #I will see if there are any matches in the previous dates
            for i in range(nprev):
                date_str=dfPrev.iloc[i]["StartDate"]
                dateStartprev=datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                matches.append(dateStart==dateStartprev)
            is_new=not bool(sum(matches))
        else:
            is_new=True
        # I only upgrade the Id number if this request is a new request
        if is_new:
            # I upgrade the ID with a "series" number
            request_id=int(str(request_id)+(str(nprev+1)))

        # I look for the duration in the past dataframe
        try:
            duration = int((dfOld[dfOld.Id==request_id_found].Duration).tolist()[0])
        except:
            #If this fails, just set the duration to 60 min for safety
            duration = 60
        dateEnd = dateStart + datetime.timedelta(minutes=duration)    

        
    else:
            duration = int(re.search('Lesson Duration: (.*)minutes',body).group(1))
            student_name = re.search('Student Name:(.*)\r',body).group(1)
            request_id=int(re.search('Request ID: (.*)\r',body).group(1))
            
            if duration>0:
                date_req=re.search('First Choice: (.*)\r',body).group(1)
                date_req_splt = date_req.split()
                time = date_req_splt[4]
                year = date_req_splt[3]
                day = date_req_splt[2][:-1]
                month_str = date_req_splt[1]
                month_dict = {"Jan":1, "Feb":2, "Mar":3, "Apr":4, "May":5, "Jun":6, "Jul":7, "Aug":8, "Sep":9, "Oct":10, "Nov":11, "Dec":12}
                month = month_dict[month_str]
                date_req_str = " ".join([str(month),day,year,time])
            
                dateStart = datetime.datetime.strptime(date_req_str, '%m %d %Y %H:%M')
                dateEnd = dateStart + datetime.timedelta(minutes=duration)  
            else:
                dateStart = datetime.datetime.today()
                dateEnd = datetime.datetime.today()
                
                
            

    
    return student_name, dateStart, dateEnd, duration, request_id

def request_info_IT(body):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    # Load IT lesson info
    dfLessonsIT=pd.read_csv(dir_path+"/INFO-Current-Lessons-Italki.csv")

    student_name = re.search('Student:(.*)Member ID',body).group(1)
    student_name= " ".join(student_name.split()[0:2])
    date_req=re.search("Lesson Date/Time:(.*)UTC",body).group(1)
    date_req_splt = date_req.split()
    time = date_req_splt[4]
    year = date_req_splt[3]
    day = date_req_splt[2][:-1]
    month_str = date_req_splt[1]
    date_req_str = " ".join([month_str,day,year,time])
    request_id=int(re.search("Lesson ID: (.*)\r",body).group(1))
    dateStart = datetime.datetime.strptime(date_req_str, '%b %d %Y %H:%M')
    lesson_name=re.search("Course Name: (.*)\r",body).group(1)
    # Correct the "Sesión de prueba" error (this is what the mail says intead of Trial lesson)
    if ("prueba" in lesson_name):
        lesson_name = "Triallesson"
    price = float(re.search("Price: (.*)USD",body).group(1)[1:])

    # Find duration
    # I first identify the lesson by the name (I remove spaces for robustness)
    lesson_list_merged=["".join(i.split()) for i in  dfLessonsIT.LessonName.tolist()]
    matchname=["".join(lesson_name.split())==i for i in lesson_list_merged]
    dfLessonsWithSameName=dfLessonsIT[matchname]
    pricesWithSameName = np.asarray(dfLessonsWithSameName.Price.tolist())
    #I find the duration by looking at the most similar price (robust against price changes)
    duration = float(dfLessonsWithSameName.iloc[np.argmin(abs(price-pricesWithSameName))].Duration)
    dateEnd = dateStart + datetime.timedelta(minutes=duration)
    
    return student_name, dateStart, dateEnd, duration, request_id
    
    
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

def send_mail_calendar_change(platform_to_modify,student_name,status,date,time,duration,before_file,after_file):
    
    #The mail addresses and password
    sender_address = 'project.owl.watcher@gmail.com'
    sender_pass = "aujlkjdbifsdfyyr"
    receiver_address = 'carmen.doncel.arauzo@gmail.com'
    
    if platform_to_modify=="CafeTalk":
        platform_requested = "Italki"
    else:
        platform_requested = "CafeTalk"
        
    status_dict = {1:"Parece que todo fue bien.",\
               2: "Parece que esta franja ya estaba bloqueada, así que no hice nada.",\
               -2:"Aparentemente, algo fue mal. Por favor, comprueba las capturas y el horario en "+platform_to_modify,\
               3:"Parece que esta hora se superpone con más de una clase. Mejor configúralo personalmente"}
    
    strFrom = sender_address
    strTo = receiver_address

    # Create the root message and fill in the from, to, and subject headers
    msgRoot = MIMEMultipart('related')
    msgRoot['Subject'] = 'Petición de '+student_name+' en '+platform_requested+'--> bloqueo en '+platform_to_modify
    msgRoot['From'] = "Proyecto Búho"
    msgRoot['To'] = strTo
    msgRoot.preamble = 'This is a multi-part message in MIME format.'

    # Encapsulate the plain and HTML versions of the message body in an
    # 'alternative' part, so message agents can decide which they want to display.
    msgAlternative = MIMEMultipart('alternative')
    msgRoot.attach(msgAlternative)

    msgText = MIMEText('This is the alternative plain text message.')
    msgAlternative.attach(msgText)

    # Example with image: We reference the image in the IMG SRC attribute by the ID we give it below
    msgText = MIMEText('¡Hoot hooot!<br><br> ¡¡Acabo de cazar una petición de  <b> <i>'+\
                       student_name+'</i></b> en '+platform_requested+'!! <br>\
                       <b>Fecha de la clase</b>: '+date+' a las  '+time+'.<br>\
                       <b>Duración</b>: '+duration+' minutos.<br>\
                       He tratado de bloquear esas horas en '+platform_to_modify+'.<br>\
                       Resultado= ('+str(status)+'): '+status_dict[status]+'\
                       <br><br> Captura del "antes": \
                       <br><img src="cid:image_before" width="500" height="250" border="0" \
    style="border:0; outline:none; class=center; text-decoration:none; display:block;"><br>\
    <br><br> Captura del "después": \
                       <br><img src="cid:image_after" width="500" height="250" border="0" \
    style="border:0; outline:none; class=center; text-decoration:none; display:block;"><br>\
    ', 'html')
    msgAlternative.attach(msgText)

    # Let us attached the BEFORE and AFTER screenshots!
    # === BEFORE ======
    fp = open(before_file, 'rb')
    msgImage = MIMEImage(fp.read())
    fp.close()
    # Define the image's ID as referenced above
    msgImage.add_header('Content-ID', '<image_before>')
    msgRoot.attach(msgImage)
    fp = open(after_file, 'rb')
    msgImage2 = MIMEImage(fp.read())
    fp.close()
    # Define the image's ID as referenced above
    msgImage2.add_header('Content-ID', '<image_after>')
    msgRoot.attach(msgImage2)

    #Create SMTP session for sending the mail
    session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
    session.starttls() #enable security
    session.login(sender_address, sender_pass) #login with mail_id and password

    session.sendmail(strFrom, strTo, msgRoot.as_string())
    session.quit()

