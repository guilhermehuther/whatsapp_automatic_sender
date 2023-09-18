from random import uniform
from time import sleep
import os
from tkinter import *
from tkinter import filedialog

import pandas as pd

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.wait import WebDriverWait
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

import requests
from bs4 import BeautifulSoup
import re
import wget
import os
import sys
import shutil

dir_path = os.path.dirname(__file__)

def send_messages(temp_file_count: bool = True,
                  waiting_time: int = 30,
                  start_wait_time: int = 60,
                  update_chrome_driver = False) -> int:
    """ 
    Send automatic messages in whatsapp
    
    Parameters
    ----------   
    temp_file_count: bool
        If True, the count of interations on the csv will be saved in a temporary file and used in the next execution. 
        If False, the count will be reset to zero.
    waiting_time: int
        In seconds set the waiting time for objects to be shown in whatsapp.
        Change basead on the speed of your internet connection and hardware.
        Set for more if you have less perfomance or less if you have more. 
    start_wait_time: int 
        Time of waiting after the whatsapp web page is opened to load the messages.
        Change basead on the speed of your internet connection and hardware.
    update_chrome_driver: bool
        If True, reinstall the chrome and chromedriver. Only use if having trouble with version.
        If False, do nothing
    
    Return
    ----------
    count: int
        Count of interations on the csv/dataframe.
    """
    
    df, driver, count, filepath = _build(temp_file_count, start_wait_time, update_chrome_driver)
    
    wait = WebDriverWait(driver, waiting_time)

    flag_new_chat = False
    
    while count < df.shape[0]:
        print(f"Current position {count} of {df.shape[0]}.")
        
        text = df['Message'].iloc[count]
        image = df['photo_path'].iloc[count]
        
        if not flag_new_chat:
            wait.until(EC.element_to_be_clickable((By.XPATH, f'//*[@data-icon="new-chat"]'))).click()
            
        wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/div/div[3]/div[1]/span/div/span/div/div[1]/div/div[2]/div/div[1]')))
        new_message_box = driver.find_element(By.XPATH, '//*[@role="textbox"]')
        new_message_box.send_keys(Keys.CONTROL, "a" + Keys.DELETE)
        new_message_box.send_keys(df['NumberOrGroup'].iloc[count])
        sleep(5) 
        
        try:
            buttons = driver.find_elements(By.XPATH, '//*[@role="button"]')
            reg = re.compile("^(" + df['NumberOrGroup'].iloc[count] + "|\+\d{2} \d{2} \d{4}-\d{4})$")
            button = [yy for yy, y in enumerate([re.findall(reg, x.text) for x in buttons]) if y]
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable(buttons[button[0]])).click()
            flag_new_chat=False
            sleep(3)
        except:
            count = _set_current_count(count, filepath)
            flag_new_chat=True
            continue
         
        if pd.isna(image):
            wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[1]')))
            text_box = driver.find_element(by = By.XPATH, value='//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[1]')
                        
        else:
            try:
                wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[1]/div[2]/div/div'))).click()

                wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[1]/div[2]/div/div'))).click()

                image_box = driver.find_element(by = By.XPATH, value='//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime"]')
                image = fr"{image}"
                image_box.send_keys(image)

                wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div/div/div[3]/div[2]/span/div/span/div/div/div[2]/div/div[1]/div[3]/div/div/div[2]/div[1]/div[1]/p')))
                
                text_box = driver.find_element(by=By.XPATH, value='//*[@id="app"]/div/div/div[3]/div[2]/span/div/span/div/div/div[2]/div/div[1]/div[3]/div/div/div[2]/div[1]/div[1]/p')    
            except Exception as e:
                # print(e) # FOR DEBUGGING
                count = _set_current_count(count, filepath)
                continue
                
            wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/div/div[3]/div[2]/span/div/span/div/div/div[2]/div/div[2]/div[2]/div/div')))
            
        for letter in text:
            sleep(uniform(0.05, 0.125))
            if letter == "&":
                text_box.send_keys(Keys.SHIFT + Keys.ENTER)
            else:
                text_box.send_keys(letter)
        
        text_box.send_keys(Keys.ENTER)
        
        count = _set_current_count(count, filepath)
        
        sleep(5)        
        
        os.system('cls||clear')
    
    print("Finished sending messages.")
    
    return count


def _build(temp_file_count, start_wait_time, update_chrome_driver) -> tuple:
    filepath, df = _file_handler()
        
    if temp_file_count:
        count_path = os.path.join(dir_path, filepath)

        if os.path.isfile(count_path):
            count = _get_current_count(filepath)
        else:
            count = _set_current_count(0, filepath, create=True)
    else:
        count = _set_current_count(0, filepath, create=True)
    
    driver = _get_browser(update_chrome_driver)

    driver.get("https://web.whatsapp.com")
    WebDriverWait(driver, 1_000_000).until(EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div/div/div[4]/header')))
    
    print(f'Waiting {start_wait_time} seconds for messages to load.')
    sleep(start_wait_time)
    os.system('cls||clear')
    
    return df, driver, count, filepath


def _get_current_count(filepath) -> int:
    count_path = os.path.join(dir_path, filepath)

    return int(open(count_path, 'r').read())


def _set_current_count(count, filepath, create = False) -> int:
    if create:
        count = 0
    else:
        count += 1
    
    count_path = os.path.join(dir_path, filepath)
    
    with open(count_path, 'w') as file:
        file.write(f'{count}')
    
    return count


def _file_handler() -> pd.DataFrame:
    filepath = filedialog.askopenfilename(
        title="Open file",
        filetypes=(
            (".csv file","*.csv"),
            ("all files","*.*")
        )
    )
    
    return filepath.split('/')[-1].split('.')[0] + '.txt', pd.read_csv(os.path.join(dir_path, filepath), sep = ';', dtype=str)


def _get_chrome_driver():
    if sys.platform.startswith("linux"): 
        op_sys = "linux"
    elif sys.platform == "darwin":
        op_sys = "mac"    
    elif os.name == "nt":
        op_sys = "win64"   

    soup = BeautifulSoup(requests.get("https://googlechromelabs.github.io/chrome-for-testing/#stable").text, 'html.parser')

    link_chrome, link_chromedriver = [z for z in [re.findall(f'.*{op_sys}.*', y) for y in [re.findall('https.*?.zip', str(x)) for x in soup.find(id="stable").find_all('tr')][0]] if z]

    dir_chrome = wget.download(link_chrome[0], out=dir_path)
    dir_chromedriver = wget.download(link_chromedriver[0], out=dir_path)

    path_chrome = os.path.join(dir_path, dir_chrome)
    path_chromedriver = os.path.join(dir_path, dir_chromedriver)

    shutil.unpack_archive(path_chrome, extract_dir=dir_path)
    shutil.unpack_archive(path_chromedriver, extract_dir=dir_path)

    os.remove(path_chrome)
    os.remove(path_chromedriver)
    
    return


def _get_chrome_paths():
    path_chrome, path_chromedriver = [os.path.join(dir_path, y[0]) for y in [re.findall(".*chrome.*", x) for x in os.listdir(dir_path)] if y]
    return path_chrome, path_chromedriver

def _get_browser(update_chrome_driver):
    if update_chrome_driver:
        try:
            path_chrome, path_chromedriver = _get_chrome_paths()
            os.remove(path_chrome)
            os.remove(path_chromedriver)
        except:
            pass
        
    try:
        path_chrome, path_chromedriver = [os.path.join(dir_path, y[0]) for y in [re.findall(".*chrome.*", x) for x in os.listdir(dir_path)] if y]
    except:
        _get_chrome_driver()
        path_chrome, path_chromedriver = [os.path.join(dir_path, y[0]) for y in [re.findall(".*chrome.*", x) for x in os.listdir(dir_path)] if y]

    options = webdriver.ChromeOptions()
    
    service = Service(os.path.join(path_chromedriver, 'chromedriver.exe'))

    options.binary_location = os.path.join(path_chrome, 'chrome.exe')

    profile = os.path.join(dir_path, "profile")
    
    options.add_argument('--log-level=3')
    options.add_argument("--start-maximized")
    options.add_argument(
        r"user-data-dir={}".format(profile))
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/99.0.4844.84 Safari/537.36")

    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("excludeSwitches", ["disable-popup-blocking"])
    options.add_experimental_option('useAutomationExtension', False)

    browser = webdriver.Chrome(options=options, service=service)
    
    browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """

    Object.defineProperty(navigator, 'webdriver', {

    get: () => undefined

    })

    """

    })
    
    browser.execute_cdp_cmd('Network.setUserAgentOverride',
                            {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                            'like Gecko) Chrome/83.0.4103.53 Safari/537.36'})
    
    return browser