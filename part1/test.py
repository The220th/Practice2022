# -*- coding: utf-8 -*-

from selenium import webdriver
import time
import os
import sys
import fake_useragent
from selenium.webdriver.common.by import By
import requests

class Global():
    options = None
    webdriver = None
    cur_user_agent = None

def writeFileB(fileName : str, b : bytes):
    with open(fileName, "wb") as binary_file:
        binary_file.write(b)

def swait(how_secs : float):
    #time.sleep(how_secs)
    Global.webdriver.implicitly_wait(how_secs)

def preready():
    fuag = fake_useragent.UserAgent()
    Global.cur_user_agent = fuag.random
    
    Global.options = webdriver.FirefoxOptions()
    Global.options.set_preference("general.useragent.override", Global.cur_user_agent)
    #old
    #Global.options.set_preference("general.useragent.override", "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.2; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0)")
    Global.options.set_preference("dom.webdriver.enabled", False)
    # Global.options.headless = True

    # https://github.com/mozilla/geckodriver
    Global.webdriver = webdriver.Firefox(
        executable_path="./geckodriver",
        options=Global.options
    )

def unhide(webElement):
    wd = Global.webdriver
    script="""arguments[0].style.opacity=1;
arguments[0].style['transform']='translate(0px, 0px) scale(1)';
arguments[0].style['MozTransform']='translate(0px, 0px) scale(1)';
arguments[0].style['WebkitTransform']='translate(0px, 0px) scale(1)';
arguments[0].style['msTransform']='translate(0px, 0px) scale(1)';
arguments[0].style['OTransform']='translate(0px, 0px) scale(1)';
return true;"""
    wd.execute_script(script, webElement)

def removeElementByClass(className : str):
    wd = Global.webdriver
    script = f"return document.getElementsByClassName({className})[0].remove();"
    wd.execute_script(script)

if __name__ == '__main__':
    preready()
    wd : webdriver.Firefox = Global.webdriver

    pdfFilePath = os.path.abspath("./cechov_rasskazy_1886.pdf")

    fileLink = None

    try:
        #wd.get("https://browser-info.ru")
        wd.get("https://www.ilovepdf.com/ru/pdf_to_word")
        swait(10)
        # https://selenium-python.readthedocs.io/locating-elements.html
        in_button = wd.find_element(By.CSS_SELECTOR, "input[type=file]")
        #in_button = wd.find_element(By.XPATH, "//*[@type=\"file\"]")
        print(in_button)
        unhide(in_button)
        input()
        
        in_button.send_keys(pdfFilePath)
        '''
        <input id="html5_1g8dsoqacpmgms23es1r0l1t874" 
        type="file" style="font-size: 999px; opacity: 0; 
        position: absolute; top: 0px; left: 0px; width: 100%; 
        height: 100%;" multiple="" accept="" tabindex="-1">
        '''
        # fckingAlert = wd.find_element(By.CLASS_NAME, "browser-alert")
        # if(fckingAlert.size() != 0):
        #     removeElementByClass("browser-alert")
        # input()

        startButton = wd.find_element(By.ID, "processTask")
        startButton.click()

        input()

        href = wd.find_element(By.ID, "pickfiles").get_attribute("href")
        print(href)
        fileLink = href

    except Exception as ex:
        print(ex)
    finally:
        wd.close()
        wd.quit()

    r = requests.get(f"{fileLink}")
    docx = r.content
    writeFileB("out.docx", docx)
