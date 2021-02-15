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
from functionscafetalk import *
from functions_mail import *

import os 
dir_path = os.path.dirname(os.path.realpath(__file__))


statusItalki = 1
student_name= "Test"
date_lesson = "1//02/2021"
time_lesson = "20:00"
duration = "20"
before_ss = dir_path+"/Screenshots/error-robot.jpg"
after_ss = dir_path+"/Screenshots/error-robot.jpg"

send_mail_calendar_change("Italki",student_name,statusItalki,date_lesson,time_lesson,duration,before_ss,after_ss)


