# -*- coding: UTF-8 -*-
# import libraries
import requests
from bs4 import BeautifulSoup
import selenium
from selenium import webdriver
import matplotlib.pyplot as plt
import time
import math
import pandas as pd
import re
import numpy as np
import datetime
import os 


def find_current_date(driver):
    # This function tells us  month and year of the calendar currently displayed
    
    monthDict = dict([('enero',1),('febrero', 2),("marzo", 3)\
          ,('abril',4),('mayo',5),('junio',6),('julio',7)\
          ,('agosto',8),('septiembre',9),('octubre',10)\
          ,('noviembre',11),('diciembre',12)])

    
    titleMonth=driver.find_element_by_class_name\
("AvailabilityTime-month-title").text
    year_curr_str=titleMonth.split()[-1]
    month_curr_str=titleMonth.split()[0]
    month_current = monthDict[month_curr_str]
    year_current = int(year_curr_str)
    
    return month_current, year_current

def TimesTimeslot(timeslot):
    left_menu=timeslot.find_element_by_class_name("TimeSlot-menu-left")
    right_menu=timeslot.find_element_by_class_name("TimeSlot-menu-right")
    time_initial=left_menu.find_element_by_class_name("menu-selected").text
    time_final=right_menu.find_element_by_class_name("menu-selected").text

    hour_initial=int(time_initial.split(":")[0])
    minute_initial = int(time_initial.split(":")[1])

    hour_final=int(time_final.split(":")[0])
    minute_final= int(time_final.split(":")[1])
    
    init_slot_time = datetime.timedelta(hours=hour_initial, minutes=minute_initial)
    final_slot_time = datetime.timedelta(hours=hour_final, minutes=minute_final)
    
    return init_slot_time, final_slot_time
    
    
def TimesTimeslotString(timeslot):
    left_menu=timeslot.find_element_by_class_name("TimeSlot-menu-left")
    right_menu=timeslot.find_element_by_class_name("TimeSlot-menu-right")
    time_initial=left_menu.find_element_by_class_name("menu-selected").text
    time_final=right_menu.find_element_by_class_name("menu-selected").text

    return time_initial, time_final

def SetTimeInMenu(menu,time_str):
    menu.find_element_by_class_name("arrow-down").click()
    time.sleep(1)
    items=menu.find_elements_by_class_name("menu-item")
    dropdowntimes = []
    for i in range(len(items)):
        dropdowntimes.append(items[i].text)

    # Find the element with the time, and click it
    indextime=dropdowntimes.index(time_str)
    item = items[indextime]
    item.click()

def request_info_IT_web():

    print("Retrieving new lesson request from Italki website")
    ## ============ NEW FUNCTION: We extract info from Italki website
    
    urlpage= 'https://teach.italki.com/?hl=es'
    driver = webdriver.Firefox()
    # get web page
    driver.get(urlpage)

    time.sleep(2)

    # Click "Iniciar sesión"
    driver.find_element_by_xpath("//span[text()='Iniciar sesión']").click()

    # Introducir credenciales
    username = driver.find_element_by_id("username_id")
    username.clear() # Not sure what this is for
    username.send_keys("carmen.doncel.arauzo@gmail.com")

    time.sleep(0.5)

    password = driver.find_element_by_id("password_id")
    password.clear() # Not sure what this is for
    password.send_keys("Shenyixin00")

    driver.find_element_by_id("login").click()
    time.sleep(3)

    try:
        driver.find_element_by_xpath("//span[text()='Continuar']").click()
    except:
        pass


    list_class_info = []

    index_block = 0 # I look at the first block, where all the new classes appear
    #driver.get("https://teach.italki.com/dashboard") # I don't really need to do this, it enters directly in dashboard
    time.sleep(2.)
    lesson_block_element=driver.find_element_by_class_name("dashboard-lesson")
    lesson_info_blocks = lesson_block_element.find_elements_by_class_name("lesson-info")
    accion_necesaria_element=lesson_info_blocks[index_block+1]
    acciones = int(accion_necesaria_element.text.split('\n')[0])
    # Si hay accion necesaria
    if acciones>0:
        time.sleep(2.)
        accion_necesaria_element.click()
        time.sleep(2.)

        # Get info about all the new classes
        class_elements=driver.find_elements_by_class_name("LessonCard-action_required")
        nclasses = len(class_elements)


        for class_element in class_elements:

            # User name and Id info
            user_and_id_info_element = class_element.find_element_by_class_name("LessonItem-userInfo-box")
            name_element = user_and_id_info_element.find_element_by_class_name("font-b")
            student_name = name_element.text
            id_element= user_and_id_info_element.find_element_by_class_name("font-l")
            request_id = int(id_element.text.split(": ")[1])

            # Class name and duration
            block_2_element = class_element.find_element_by_class_name("LessonItem-part-2")
            title = block_2_element.find_element_by_class_name("lessonInfo-title").text
            lesson_info = block_2_element.find_element_by_class_name("lessonInfo-bar").text
            duration = float(re.search('\n(.*) min', lesson_info).group(1))

            # Date and time
            date_info = class_element.find_element_by_class_name("LessonItem-p3-newTime").text.split()

            month_str=date_info[3]
            month_dict = {"ene.":1, "feb.":2, "mar.": 3, "abr.": 4, "may.":5, "jun.":5, \
                          "jul.":6, "ago.": 8, "sep.": 9, "oct.": 10, "nov.": 11, "dic.":12}
            month = month_dict[month_str]
            day=date_info[1]
            
            time_ini = date_info[5]

            current_month = datetime.date.today().month
            current_year = datetime.date.today().year

            if (month>=current_month):
                year = str(current_year)
            else:
                year = str(current_year +1)
                
            date_req_str = " ".join([str(month),day,year,time_ini])
            dateStart = datetime.datetime.strptime(date_req_str, '%m %d %Y %H:%M')
            dateEnd = dateStart + datetime.timedelta(minutes=duration)

            list_class_info.append([student_name,dateStart, dateEnd, duration, request_id])
            
            
        column_names = ["Name","StartDate","EndDate","Duration","Id"]
        dfNewIT = pd.DataFrame(list_class_info, columns=column_names)

    time.sleep(1)
    driver.quit()

    #######=================================
    
    print("Information retrieved from Italki website")
    # Info has been extracted
    # Now: 
    #
    if acciones==0:
        print("No new classes found")
        return -1 # No new classes
    else:
        print(str(acciones)+" new classes found!")
        return dfNewIT

    
def ModifyCalendarItalki(month_desired,day_desired,hour_req_ini,min_req_ini,hour_req_fin,min_req_fin,lesson_id):
    current_time_str=datetime.datetime.now().strftime("%d-%m-%Y_%H_%M")
    dir_path = os.path.dirname(os.path.realpath(__file__))
    urlpage= 'https://teach.italki.com/?hl=es'
    driver = webdriver.Firefox()
    # get web page
    driver.get(urlpage)

    time.sleep(2)

 
    driver.find_element_by_xpath("//span[text()='Iniciar sesión']").click()

    # Introducir credenciales
    username = driver.find_element_by_id("username_id")
    username.clear() # Not sure what this is for
    username.send_keys("carmen.doncel.arauzo@gmail.com")

    time.sleep(0.5)

    password = driver.find_element_by_id("password_id")
    password.clear() # Not sure what this is for
    password.send_keys("Shenyixin00")

    driver.find_element_by_id("login").click()
    time.sleep(3)

    try:
        driver.find_element_by_xpath("//span[text()='Continuar']").click()
    except:
        pass

    driver.get("https://teach.italki.com/console/lessons")
    time.sleep(3)

    # Enter in the calendar
    driver.find_element_by_xpath("//span[text()='Calendario de profesor']").click()
    time.sleep(1)
    
    
    # Find current date displayed
    month_current, year_current = find_current_date(driver)      


    # +12 en caso de que el mes deseado sea el año que viene
    # (en cuyo caso el month_desired sería menor que el current)
    if(month_desired<month_current):
        month_desired=12+month_desired

    clicks_to_desired=month_desired-month_current

    # Move to the desired month  
    for i in range(clicks_to_desired):    
        nextButton=driver.find_element_by_class_name("AvailabilityTime-month-next")
        nextButton.click()
        time.sleep(1.)

 

    # Find the desired day and click it
    driver.find_element_by_xpath("//span[text()='"+str(day_desired)+"']").click()

    time.sleep(1)
    initial_ss_filename = dir_path+"/Screenshots/initial_screenshot"+lesson_id+".png"
    driver.save_screenshot(initial_ss_filename)   
    # Analyse the "Confirm today button"
    btn_confirm_today=driver.find_element_by_class_name\
    ("apply-today")

    day_confirm_btn=btn_confirm_today.text.split()[2]
    month_confirm_btn=btn_confirm_today.text.split()[4]

    isGoodDay = int(day_confirm_btn)==day_desired

    if isGoodDay!=1:
        raise ValueError("El calendario no se ha movido a la posición indicada")

        
    # Curate the times for Italki time-slots
    if(min_req_ini<30):
        min_req_ini=0
    else:
        min_req_ini=30

    if(min_req_fin>30):
        min_req_fin=0
        hour_req_fin = hour_req_fin+1
    else:
        min_req_fin=30

    time_req_ini = datetime.time(hour=hour_req_ini,minute=min_req_ini)
    time_req_fin = datetime.time(hour=hour_req_fin,minute=min_req_fin)
    time_req_ini_str = str(time_req_ini)[0:5]
    time_req_fin_str = str(time_req_fin)[0:5]
    
    # Extract timeslots
    timeslot_list = driver.find_elements_by_class_name("TimeSlot")

    n_timeslots = len(timeslot_list)

    init_req_time = datetime.timedelta(hours=hour_req_ini, minutes=min_req_ini)
    fin_req_time = datetime.timedelta(hours=hour_req_fin, minutes=min_req_fin)

    # 1-Identify timeslot containing initial time
    index_slot_initial = -1 # Default value, indicates no overlap
    for i in range(n_timeslots):
        timeslot = timeslot_list[i]
        init_slot_time, final_slot_time = TimesTimeslot(timeslot)

        if (init_req_time>=init_slot_time)&(init_req_time<=final_slot_time):
            index_slot_initial = i
            break

    # 2-Identify timeslot containing final time
    index_slot_final = -1
    for i in range(n_timeslots):
        timeslot = timeslot_list[i]
        init_slot_time, final_slot_time = TimesTimeslot(timeslot)

        if (fin_req_time>=init_slot_time)&(fin_req_time<=final_slot_time):
            index_slot_final = i
            break 

    if (index_slot_initial==-1)&(index_slot_final==-1):
        #Case 1: No overlap
        #Do nothing: end program
        pass
        
    # CASO 2: The END of the class overlaps with one slot.   
    #Action: Move STARTING time of the slot to the final time requested
    elif (index_slot_initial==-1)&(index_slot_final!=-1):
        
        timeslot = timeslot_list[index_slot_final]
        menu=timeslot.find_element_by_class_name("TimeSlot-menu-left")
        SetTimeInMenu(menu,time_req_fin_str)

    # CASO 3: The START of the class overlaps with one slot.   
    #Action: Move ENDING time of the slot to the initial time requested
    elif (index_slot_initial!=-1)&(index_slot_final==-1):
        
        timeslot = timeslot_list[index_slot_initial]
        menu=timeslot.find_element_by_class_name("TimeSlot-menu-right")
        SetTimeInMenu(menu,time_req_ini_str)    

    # CASO 4: The requested class lies WITHIN one single slot
    #Action: 1- Reduce slot before requested time. 2-Create new slot AFTER the requested time.  
    elif (index_slot_initial==index_slot_final):
        

        # 1- Reduce FINAL time of the block to the initial-requested
        timeslot = timeslot_list[index_slot_initial]


        final_time_slot=TimesTimeslotString(timeslot)[1] # Save the final time of the slot!    
        menu=timeslot.find_element_by_class_name("TimeSlot-menu-right")
        SetTimeInMenu(menu,time_req_ini_str)  

        # 2- Create a new slot
        driver.find_element_by_class_name("add-time-slot").click()

        #Re-define time_slots since there is a new one
        timeslot_list = driver.find_elements_by_class_name("TimeSlot")
        # The new slot must follow the slot we just modified
        timeslot = timeslot_list[index_slot_initial+1]

        #Set initial time
        menu=timeslot.find_element_by_class_name("TimeSlot-menu-left")
        SetTimeInMenu(menu,time_req_fin_str)  
        time.sleep(1)
        #Set final time
        menu=timeslot.find_element_by_class_name("TimeSlot-menu-right")
        SetTimeInMenu(menu,final_time_slot)  

    # CASE 5: We have two overlapping blocks
    else:
        timeslot = timeslot_list[index_slot_final]
        menu=timeslot.find_element_by_class_name("TimeSlot-menu-left")
        SetTimeInMenu(menu,time_req_fin_str)

        time.sleep(1)

        timeslot = timeslot_list[index_slot_initial]
        menu=timeslot.find_element_by_class_name("TimeSlot-menu-right")
        SetTimeInMenu(menu,time_req_ini_str)    

    time.sleep(2) 
    # Save changes
    # Save a final screenshot of the event
    final_ss_filename = dir_path+"/Screenshots/final_screenshot_IT_"+lesson_id+".png"
    driver.save_screenshot(final_ss_filename);
    driver.find_element_by_class_name("apply-today").click()

    time.sleep(2) 

    driver.quit()
    return 1, initial_ss_filename, final_ss_filename
