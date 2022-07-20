# -*- coding: utf-8 -*-

from selenium import webdriver
import time
import datetime
import os
import sys
import fake_useragent
from selenium.webdriver.common.by import By
import requests
from selenium.webdriver.firefox.service import Service as fireService

class Global():
    options = None
    webdriver = None
    cur_user_agent = None
    path_to_pdf = "in.pdf"
    path_to_docx = "out.docx"

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
    #old=
    #Global.options.set_preference("general.useragent.override", "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.2; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0)")
    Global.options.set_preference("dom.webdriver.enabled", False)
    Global.options.headless = True

    
    Global.webdriver = webdriver.Firefox(
        service=chooseDriver(),
        options=Global.options
    )

def chooseDriver() -> "fireService":
    # https://github.com/mozilla/geckodriver
    if(sys.platform == "linux"): #or platform == "linux2"
        driverPath = os.path.abspath("./webdrivers/geckodriver-linux")
    elif(sys.platform == "win32"):
        driverPath = os.path.abspath("./webdrivers/geckodriver-windows.exe")
    elif(sys.platform == "darwin"):
        driverPath = os.path.abspath("./webdrivers/geckodriver-macos")
    else:
        print("Cannot load driver")
        raise Exception("Cannot load driver")
    ser = fireService(driverPath)
    return ser

def unhide(webElement):
    # https://barancev.github.io/how-to-attach-file-to-invisible-field/
    wd = Global.webdriver
    script="""arguments[0].style.opacity=1;
arguments[0].style['transform']='translate(0px, 0px) scale(1)';
arguments[0].style['MozTransform']='translate(0px, 0px) scale(1)';
arguments[0].style['WebkitTransform']='translate(0px, 0px) scale(1)';
arguments[0].style['msTransform']='translate(0px, 0px) scale(1)';
arguments[0].style['OTransform']='translate(0px, 0px) scale(1)';
return true;"""
    wd.execute_script(script, webElement)

def plog(s : str):
    time_str = datetime.datetime.now().strftime("[%y.%m.%d %H:%M:%S.%f]")
    print(f"{time_str} {s}")

def removeElementByClass(className : str):
    wd = Global.webdriver
    script = f"return document.getElementsByClassName({className})[0].remove();"
    wd.execute_script(script)

if __name__ == '__main__':
    argc = len(sys.argv)
    if(argc != 2):
        print(f"Syntax error. Excepted: \"python {sys.argv[0]} {'{'}path_to_pdf{'}'}\". ")
        exit()
    else:
        path_to_pdf = os.path.abspath(sys.argv[1])
        if(len(path_to_pdf) < 5 or path_to_pdf[-4:] != ".pdf"):
            print(f"File \"{path_to_pdf}\" is not pdf file. ")
            exit()
        if(os.path.exists(path_to_pdf) == False):
            print(f"File \"{path_to_pdf}\" does not exists. ")
            exit()
        path_to_docx = path_to_pdf[:-4] + ".docx"
        Global.path_to_pdf = path_to_pdf
        Global.path_to_docx = path_to_docx
    preready()
    wd : webdriver.Firefox = Global.webdriver

    pdfFilePath = Global.path_to_pdf

    fileLink = None

    try:
        #wd.get("https://browser-info.ru")
        plog(f"Going to site \"{'https://www.ilovepdf.com/ru/pdf_to_word'}\"...")
        wd.get("https://www.ilovepdf.com/ru/pdf_to_word")
        swait(100)

        plog(f"Trying find imput element...")
        # https://selenium-python.readthedocs.io/locating-elements.html
        in_button = wd.find_element(By.CSS_SELECTOR, "input[type=file]")
        
        plog(f"Trying \"unhide\" input element...")
        # https://habr.com/ru/post/497922/
        unhide(in_button)
        swait(100)
        
        plog(f"Trying input in input element path to file \"{pdfFilePath}\"...")
        in_button.send_keys(pdfFilePath)
        '''
        <input id="html5_???" 
        type="file" style="font-size: 999px; opacity: 0; 
        position: absolute; top: 0px; left: 0px; width: 100%; 
        height: 100%;" multiple="" accept="" tabindex="-1">
        '''
        # fckingAlert = wd.find_element(By.CLASS_NAME, "browser-alert")
        # if(fckingAlert.size() != 0):
        #     removeElementByClass("browser-alert")
        # input()

        plog(f"Trying find \"processTask\" button...")
        startButton = wd.find_element(By.ID, "processTask")
        plog(f"Trying click to \"processTask\" button...")
        startButton.click()

        while(True):
            plog(f"Waiting while file converting...")
            #swait(100) #&!&!??!?!
            time.sleep(10)

            plog(f"Okey. Getting docx file download link...")
            href = wd.find_element(By.ID, "pickfiles").get_attribute("href")
            plog(f"Download link was found: \"{href}\". ")
            fileLink = href
            if(href[:5] == "https"): # too sad=/
                plog("The link is correct. I think so...")
                break
            else:
                plog("Wait... The link is not ready yet as the file has not been converted yet mb. I'll try to wait some more.")
        plog(f"Trying close browser as soon as possible...")

    except Exception as ex:
        print(ex)
    finally:
        plog(f"Trying close browser correctly...")
        wd.close()
        wd.quit()
        plog(f"Browser closed correctly. I think so... ")

    plog(f"Trying to download file from \"{fileLink}\" on computer as \"{Global.path_to_docx}\"...")
    r = requests.get(f"{fileLink}")
    docx = r.content
    plog(f"File downloaded from \"{fileLink}\". ")
    plog(f"Trying save file to \"{Global.path_to_docx}\"...")
    writeFileB(Global.path_to_docx, docx)
    plog(f"File saved to \"{Global.path_to_docx}\"")
    plog(f"========== Done ==========")
