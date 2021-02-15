# -*- coding: UTF-8 -*-
# import libraries
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import matplotlib.pyplot as plt
import time
import math
import pandas as pd
import re
from tqdm import tqdm
import numpy as np
import datetime
import os 


def ModifyCalendarCafeTalk(month_desired,day_desired,hour_req_ini,min_req_ini,hour_req_fin,min_req_fin,year,lesson_id):

    dir_path = os.path.dirname(os.path.realpath(__file__))
    status = -1 # This will become 1 if submission is sucessful. Returned by the function.
    startDate = str(year)+"-"+str(month_desired).zfill(2)+"-"+str(day_desired).zfill(2)
    finalDate = startDate

    startHourInt = hour_req_ini
    startMinuteInt = min_req_ini
    startHour = str(startHourInt).zfill(2)
    startMinute = str(startMinuteInt).zfill(2)
    
    endHourInt = hour_req_fin
    endMinuteInt = min_req_fin
    endHour = str(endHourInt).zfill(2)
    endMinute = str(endMinuteInt).zfill(2)
    
    
    
    current_time_str=datetime.datetime.now().strftime("%d-%m-%Y_%H_%M")
    urlpage= 'https://cafetalk.com/login/?t=p&lang=en'
    driver = webdriver.Firefox()
    # get web page
    driver.get(urlpage)
    time.sleep(1)

    # Login in the website
    username = driver.find_element_by_id("email")
    username.clear() # Not sure what this is for
    username.send_keys("carmen.doncel.arauzo@gmail.com")

    password = driver.find_element_by_name("passwd")
    password.clear()
    password.send_keys("Shenyixin00")
    driver.find_element_by_id("submit_btn").click()
    time.sleep(10)

    # Go to schedule
    driver.get('https://cafetalk.com/dashboard/tutor/schedule/additional/?lang=en')
    time.sleep(5)


    # ====== Start date=========
    # We cheat to remove the read-only attribute
    driver.execute_script("document.getElementsByClassName('manual-data-period-start-date')[0].removeAttribute('readonly')");
    # We enter the desired input date
    input_date_field = driver.find_element_by_class_name("manual-data-period-start-date")
    input_date_field.clear()
    input_date_field.send_keys(startDate)

    #Selection initial time from dropdown
    driver.find_element_by_xpath("//select[@name='manual-data-period-start-hour']/option[@value="+startHour+"]").click()
    time.sleep(0.2)
    driver.find_element_by_xpath("//select[@name='manual-data-period-start-minute']/option[@value="+startMinute+"]").click()
    time.sleep(0.2)




    # ====== End date=========
    # We cheat to remove the read-only attribute
    driver.execute_script("document.getElementsByClassName('manual-data-period-end-date')[0].removeAttribute('readonly')");
    # We enter the desired input date
    input_date_field = driver.find_element_by_class_name("manual-data-period-end-date")
    input_date_field.clear()
    input_date_field.send_keys(finalDate)

    #Selection final time from dropdown
    driver.find_element_by_xpath("//select[@name='manual-data-period-end-hour']/option[@value="+endHour+"]").click()
    time.sleep(0.2)
    driver.find_element_by_xpath("//select[@name='manual-data-period-end-minute']/option[@value="+endMinute+"]").click()
    time.sleep(0.2)
    
    # Take a snapshot
    initial_ss_filename = dir_path+"/Screenshots/initial_screenshot_CT-"+lesson_id+".png"
    try:
        driver.save_screenshot(initial_ss_filename);
    except:
        pass
    
    # Submit button "Next"
    driver.find_element_by_class_name("btn-success").click()
    time.sleep(0.1)
    # Select Blocked type
    driver.find_element_by_xpath("//select[@name='type']/option[@value='blocked']").click()
    time.sleep(0.1)
    
    try:
        # Submit
        driver.find_element_by_class_name("schedule-submit-btn").click()
        status = 1
    except:
        print("Capturé el error!")
    time.sleep(6)

    # Take a snapshot
    final_ss_filename = dir_path+"/Screenshots/final_screenshotCT-"+lesson_id+".png"
    try:
        driver.save_screenshot(final_ss_filename);
    except:
        status =2 # Failure at the point of submitting
   
    driver.save_screenshot(final_ss_filename);
    time.sleep(0.5)
    driver.quit()
    
    return status, initial_ss_filename, final_ss_filename
