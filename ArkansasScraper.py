#pip.main(['install','requests'])
#pip.main(['install','pandas'])
#pip.main(['install','beautifulsoup4'])
#pip.main(['install','selenium'])

import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup

import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException  
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from urllib.request import urlopen


#Set up headless browser
chrome_options = webdriver.ChromeOptions()

chrome_options.add_argument("--headless")
chrome_options.binary_location = '/Applications/Google Chrome.app/'

chromedriver = '/usr/bin/chromedriver/chromedriver'
browser = webdriver.Chrome(chromedriver)

def buildUrl(county, begin_date, end_date):
    base = "https://caseinfo.aoc.arkansas.gov/cconnect/PROD/public/ck_public_qry_doct.cp_new_case_frames"
    param_text = "?" + "county_code=" + county + "&locn_code=ALL&begin_date=" + begin_date + "&end_date=" + end_date
    return base + param_text

def getPage(county, begin_date, end_date):
    url = buildUrl(county, begin_date, end_date)
    browser.get(url)
    time.sleep(3)
    soup = BeautifulSoup(browser.page_source, "lxml")

    iframes = soup.find_all('frame')
    base = "https://caseinfo.aoc.arkansas.gov/cconnect/PROD/public/"

    iframe_soup = []
    for iframe in iframes:
        response = urlopen(base + iframe.attrs['src'])
        iframe_soup.append(BeautifulSoup(response, "lxml"))
    
    return iframe_soup[1]
    
def getData(county, begin_date, end_date):
    page = getPage(county, begin_date, end_date)
    table = page.find_all("table")[0]
    rows = table.find_all("tr")

    dates = []
    ids= []
    types = []
    judges = []
    courts = []
    for row in rows:
        cols = row.find_all("td")
        if (len(cols) > 5):
            dates.append(cols[0])
            ids.append(cols[1])
            types.append(cols[2])
            judges.append(cols[3])
            courts.append(cols[4])
    
    data = pd.DataFrame(
        {'date': dates,
         'ids': ids,
         'type': types,
         'judge' : judges,
         'court' : courts
        })
        
    print(data)
        
    return page

county = "10 - CLARK"
begin_date = "02/01/2018"
end_date = "02/05/2018"
info = getData(county, begin_date, end_date)
#print(info)
#browser.close()


#case_type
#cort_code
#docket_code