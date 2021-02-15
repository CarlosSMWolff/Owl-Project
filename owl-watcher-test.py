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
from functions_mail import *
import os

dir_path = os.path.dirname(os.path.realpath(__file__))
print("=================================================")
print("\nStarting Project Owl at ")
print(datetime.datetime.now()) 

month_desired = 7
day_desired = 7
hour_req_ini = 13
min_req_ini = 0
hour_req_fin = 18
min_req_fin = 0
lesson_id = '0'
year = 2021
statusItalki, before_ss, after_ss = ModifyCalendarCafeTalk(month_desired,day_desired,hour_req_ini,min_req_ini,hour_req_fin,min_req_fin,year,lesson_id)
        
print("Status is "+str(statusItalki))
print("\nClosing Project Owl at ") 
print(datetime.datetime.now())
