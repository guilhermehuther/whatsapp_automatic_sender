from random import uniform
from time import sleep
import os
from tkinter import *
from tkinter import filedialog

import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.wait import WebDriverWait
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

dir_path = os.path.dirname(__file__)

def send_messages(temp_file_count: bool = True,
                  waiting_time: int = 30,
                  start_wait_time: int = 60) -> int:
    """ 
    Send automatic messages in whatsapp
    
    Parameters
    ----------   
    temp_file_count: bool
        If true, the count of interations on the csv will be saved in a temporary file and used in the next execution. 
        If false, the count will be reset to zero.
    waiting_time: int
        In seconds set the waiting time for objects to be shown in whatsapp.
        Change basead on the speed of your internet connection and hardware.
        Set for more if you have less perfomance or less if you have more. 
    start_wait_time: int 
        Time of waiting after the whatsapp web page is opened to load the messages.
        Change basead on the speed of your internet connection and hardware.
    
    Return
    ----------
    count: int
        Count of interations on the csv/dataframe.
    """
    
    df, driver, count, filepath = _build(temp_file_count, start_wait_time)
    
    wait = WebDriverWait(driver, waiting_time)

    while count < df.shape[0]:
        print(f"Current position {count} of {df.shape[0]}.")
        
        text = df['Message'].iloc[count]
        image = df['photo_path'].iloc[count]
        
        try:
            number_or_group = int(df['NumberOrGroup'].iloc[count])
            driver.get(f'https://web.whatsapp.com/send/?phone={str(number_or_group)}&text&type=phone_number&app_absent=0')    
        except:
            number_or_group = df['NumberOrGroup'].iloc[count]
            driver.get(f'https://web.whatsapp.com/')
            wait.until(EC.element_to_be_clickable((By.XPATH, f".//*[@title='{number_or_group}']"))).click()    
               
        if pd.isna(image):
            # NO IMAGE
            wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[1]')))
            text_box = driver.find_element(by = By.XPATH, value='//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[1]/div/div[1]')
                        
        else:
            # IMAGE
            try:
                wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[1]/div[2]/div/div'))).click()
            except:    
                count = _set_current_count(count, filepath)
                continue
            try:
                wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[1]/div[2]/div/div'))).click()
            except:
                count = _set_current_count(count, filepath)
                continue
            
            try:
                image_box = driver.find_element(by = By.XPATH, value='//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime"]')
                image = fr"{image}"
                image_box.send_keys(image)
            except:        
                count = _set_current_count(count, filepath)
                continue
        
            try:
                wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div/div/div[3]/div[2]/span/div/span/div/div/div[2]/div/div[1]/div[3]/div/div/div[2]/div[1]/div[1]/p')))
            except:        
                count = _set_current_count(count, filepath)
                continue
            
            try:      
                text_box = driver.find_element(by=By.XPATH, value='//*[@id="app"]/div/div/div[3]/div[2]/span/div/span/div/div/div[2]/div/div[1]/div[3]/div/div/div[2]/div[1]/div[1]/p')    
            except:        
                count = _set_current_count(count, filepath)
                continue
            
            wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="app"]/div/div/div[3]/div[2]/span/div/span/div/div/div[2]/div/div[2]/div[2]/div/div')))
            
            button = driver.find_element(By.XPATH, '//*[@id="app"]/div/div/div[3]/div[2]/span/div/span/div/div/div[2]/div/div[2]/div[2]/div/div')
            
        for letter in text:
            sleep(uniform(0.05, 0.125))
            text_box.send_keys(letter)
        
        if pd.isna(image):
            wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[2]/button')))
            button = driver.find_element(by = By.XPATH, value='//*[@id="main"]/footer/div[1]/div/span[2]/div/div[2]/div[2]/button/span')

        button.click()
        
        count = _set_current_count(count, filepath)
        
        sleep(uniform(5, 10))        
        
        os.system('cls')
    
    print("Finished sending messages.")
    
    return count


def _build(temp_file_count, start_wait_time) -> tuple:
    filepath, df = _file_handler()
        
    if temp_file_count:
        count_path = os.path.join(dir_path, filepath)

        if os.path.isfile(count_path):
            count = _get_current_count(filepath)
        else:
            count = _set_current_count(0, filepath, create=True)
    else:
        count = _set_current_count(0, filepath, create=True)
    
    driver = _browser_anonymous()

    driver.get("https://web.whatsapp.com")
    WebDriverWait(driver, 1_000_000).until(EC.presence_of_element_located((By.XPATH, '//*[@id="app"]/div/div/div[4]/header')))
    
    print(f'Waiting {start_wait_time} seconds for messages to load.')
    sleep(start_wait_time)
    os.system('cls')
    
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
            ("csv file","*.csv"),
            ("all files","*.*")
        )
    )
    
    return filepath.split('/')[-1].split('.')[0] + '.txt', pd.read_csv(os.path.join(dir_path, filepath), sep = ';')


def _browser_anonymous():
    options = webdriver.ChromeOptions()
    
    service = Service(os.path.join(dir_path, "chromedriver.exe"))

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
