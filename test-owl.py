import selenium
from selenium import webdriver
import time

urlpage= 'https://teach.italki.com/?hl=es'
driver = webdriver.Firefox()
time.sleep(10)
driver.quit()

