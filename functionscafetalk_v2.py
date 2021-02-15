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
import numpy as np
import datetime
import os 
from selenium.webdriver.common.alert import Alert 


def create_block(driver,startDate,startHour,startMinute,endHour,endMinute):
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
    input_date_field.send_keys(startDate) # I asume this occurs in the same day

    #Selection final time from dropdown
    driver.find_element_by_xpath("//select[@name='manual-data-period-end-hour']/option[@value="+endHour+"]").click()
    time.sleep(0.2)
    driver.find_element_by_xpath("//select[@name='manual-data-period-end-minute']/option[@value="+endMinute+"]").click()
    time.sleep(0.2)
    
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
        print("Error metiendo las horas")
        
def get_timeslot_info(blocked_slot):
    info_str=blocked_slot.text.split()
    am_pm_hours = {"am":0, "pm":12}
    month_dict = {"Jan":1, "Feb":2, "Mar":3, "Apr":4,"May":5,\
                 "Jun":6, "Jul":7, "Aug":8, "Sep":9,"Oct":10\
                 ,"Nov":11,"Dec":12}
    
    month_ini_str = info_str[0]
    month_ini = month_dict[month_ini_str]
    day_ini = int(info_str[1][0:-1])
    year_ini = int(info_str[2])
    time_ini_str = info_str[3][0:-2].split(":")
    am_pm_str = info_str[3][-2:]
    hour_ini = int(time_ini_str[0])+am_pm_hours[am_pm_str]
    min_ini = int(time_ini_str[1])

    month_fin_str = info_str[5]
    month_fin = month_dict[month_fin_str]
    day_fin = int(info_str[6][0:-1])
    year_fin = int(info_str[7])
    time_fin_str = info_str[8][0:-2].split(":")
    am_pm_str = info_str[8][-2:]
    hour_fin = int(time_fin_str[0])+am_pm_hours[am_pm_str]
    min_fin = int(time_fin_str[1])
    year = year_ini
    
    return year, month_ini, day_ini, hour_ini, min_ini, month_fin, day_fin, hour_fin, min_fin


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


    
    # Take a snapshot
    initial_ss_filename = dir_path+"/Screenshots/initial_screenshot_CT-"+lesson_id+".png"
    driver.save_screenshot(initial_ss_filename);


    # Analyse the schedule
    schedule=driver.find_element_by_class_name("additional-schedule-list")
    blocked_slots=schedule.find_elements_by_class_name("medium-8")

       
    blocked_slots_data = []

    for blocked_slot in blocked_slots:
        blocked_slots_data.append(get_timeslot_info(blocked_slot))
        
    column_names = ["Year", "Month_ini", "Day_ini", "Hour_ini","Min_ini", "Month_fin","Day_fin","Hour_fin","Min_fin"]
    blocked_slots_df = pd.DataFrame(blocked_slots_data, columns=column_names)

    year_req, month_req, day_req =  [int(x) for x in startDate.split("-")]

    match_day_mask=((blocked_slots_df.Year==year_req)&(blocked_slots_df.Month_ini==month_req)\
    &(blocked_slots_df.Day_ini==day_req)).tolist()

    nslots = len(blocked_slots)
    #I obtain a list of indexes of those blocks that match with the day requested
    index_day_match=(np.arange(nslots)[match_day_mask]).tolist()

    # Run over all possible coincidences
    overlaps = []
    cases1 = []
    cases2 = []
    cases3 = []

    for idx_match in range(len(index_day_match)):
        timeslot=blocked_slots_df.iloc[index_day_match[idx_match]]
        time_init_slot=datetime.timedelta(hours=float(timeslot.Hour_ini), minutes=float(timeslot.Min_ini))
        time_fin_slot=datetime.timedelta(hours=float(timeslot.Hour_fin), minutes=float(timeslot.Min_fin))
        time_init_req=datetime.timedelta(hours=float(startHour), minutes=float(startMinute))
        time_fin_req=datetime.timedelta(hours=float(endHour), minutes=float(endMinute))
        
        # CASE 1:
        case1=((time_init_slot <= time_init_req < time_fin_slot)&\
        (time_fin_req > time_fin_slot))
        cases1.append(case1)

        # CASE 2:
        case2 = ((time_init_slot <= time_init_req < time_fin_slot)&\
        (time_init_slot <time_fin_req <= time_fin_slot))
        cases2.append(case2)

        # CASE 3:
        case3 = ((time_init_slot < time_fin_req <= time_fin_slot)&\
        (time_init_req<time_init_slot))
        cases3.append(case3)
        
        overlaps.append(case1 or case2 or case3)
    overlaps = [int(x) for x in overlaps]

    if sum(overlaps)==0:
        #If there is NO OVERLAP: just write the block and do your thing
        create_block(driver,startDate,startHour,startMinute,endHour,endMinute)
        status = 1

    elif sum(overlaps)==1:
        # If there is one OVERLAP: go to the block where there is overlap
        overlap_index = overlaps.index(1)
        
        if cases1[overlap_index]==True:
            # Action for CASE 1
            blocked_slot_element=blocked_slots[index_day_match[overlap_index]]       
            # Delete block
            blocked_slot_element.find_element_by_class_name("icon-trash-o").click()        
            Alert(driver).accept()
            try:
                Alert(driver).accept()
            except: 
                pass
            
            time.sleep(1)
            timeslot_df = blocked_slots_df.iloc[index_day_match[overlap_index]]       
            # Redefine hours, and create new block
            startHour = str(timeslot_df.Hour_ini).zfill(2)
            startMinute = str(timeslot_df.Min_ini).zfill(2)
            create_block(driver,startDate,startHour,startMinute,endHour,endMinute)
            status = 1
            
        if cases2[overlap_index]==True:
            # Action for CASE 2
            # Do nothing
            status = 2
            
        if cases3[overlap_index]==True:
            # Action for CASE 3
            # Do nothing
            blocked_slot_element=blocked_slots[index_day_match[overlap_index]]       
            # Delete block
            blocked_slot_element.find_element_by_class_name("icon-trash-o").click()        
            Alert(driver).accept()
            try:
                Alert(driver).accept()
            except: 
                pass
            time.sleep(1)
            timeslot_df = blocked_slots_df.iloc[index_day_match[overlap_index]]       
            # Redefine hours, and create new block
            endHour = str(timeslot_df.Hour_fin).zfill(2)
            endMinute = str(timeslot_df.Min_fin).zfill(2)
            create_block(driver,startDate,startHour,startMinute,endHour,endMinute)
            status = 1    
                
    else:
        print("There was overlap with several blocks!! Check!")
        status = 3
    
    time.sleep(6)

    # Take a snapshot
    final_ss_filename = dir_path+"/Screenshots/final_screenshotCT-"+lesson_id+".png"
    driver.save_screenshot(final_ss_filename);
   
    time.sleep(0.5)
    driver.quit()
    
    return status, initial_ss_filename, final_ss_filename
