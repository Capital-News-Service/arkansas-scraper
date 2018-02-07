#pip.main(['install','requests'])
#pip.main(['install','pandas'])
#pip.main(['install','beautifulsoup4'])
#pip.main(['install','selenium'])

import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup

import time
import json
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

chromedriver = '/usr/bin/chromedriver/chromedriver'
browser = webdriver.Chrome(chromedriver, chrome_options=chrome_options)

vals={}
with open("fields.py","r") as f:
    vals = json.loads(f.read())
    
counties = vals["counties"]



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
    
    dates = []
    ids = []
    descriptions = []
    types = []
    judges = []
    courts = []
    
    table = page.find("table")
    if (table):
        rows = table.find_all("tr")

        for row in rows:
            cols = row.find_all("td")
            if (len(cols) > 5):
                dates.append(cols[0].get_text())
                ids.append(cols[1].get_text().split(" ", 1)[0]),
                descriptions.append(cols[1].get_text().split(" ", 1)[1])
                types.append(cols[2].get_text())
                judges.append(cols[3].get_text())
                courts.append(cols[4].get_text())
        
        data = pd.DataFrame(
            {'date': dates,
             'id': ids,
             'description' : descriptions,
             'type': types,
             'judge' : judges,
             'court' : courts
            })
            
        return data

    else:

        data = pd.DataFrame(
            {'date': dates,
             'id': ids,
             'description' : descriptions,
             'type': types,
             'judge' : judges,
             'court' : courts
            })

        return data

def getCase(id):
    url = "https://caseinfo.aoc.arkansas.gov/cconnect/PROD/public/ck_public_qry_doct.cp_dktrpt_frames?case_id=" + id
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

def getCaseData(id):
    page = getCase(id)

    table = page.find_all("table")
    if (table):

        rows = table[2].find_all("tr")

        for row in rows:
            cols = row.find_all("td")

            for col in cols:
                print(col.get_text())


    
def getAllData():
    end = 1990

    for begin in range(1990,2018):
        print("begin " + str(begin))
        print("end " + str(end))
        begin_date = "01/01/" + str(begin)
        end_date = "01/02/" + str(end)

        dates = []
        ids= []
        types = []
        descriptions = []
        judges = []
        courts = []

        result = pd.DataFrame(
                {'date': dates,
                 'id': ids,
                 'description' : descriptions,
                 'type': types,
                 'judge' : judges,
                 'court' : courts
                })

        for county in counties:
            result = result.append(getData(county, begin_date, end_date))
            print("county " + county)
            print(result.size)
            print(result)
            
        end = end + 1

getAllData()
#getCaseData("02DR-82-381")


#case_type
#cort_code
#docket_code