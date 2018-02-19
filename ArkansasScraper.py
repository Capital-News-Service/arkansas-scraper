# Jake Gluck - Capital News Service #


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

def scrapeDocketEntries(table):
    rows = table.find_all("tr")

    filling_dates = []
    descriptions = []
    names = []
    monetaries = []
    entries = []
    images = []

    count = 0

    #Scrape Docket Entries
    for row in rows:
       
        if (row.has_attr('valign')):
            cols1 = row.find_all('td')
            filling_dates.append(cols1[0].get_text())
            descriptions.append(cols1[1].get_text())
            names.append(cols1[2].get_text())
            monetaries.append(cols1[3].get_text().strip('\n'))

            cols2 = rows[count + 1].find_all('td')
            entries.append(cols2[1].get_text())

            cols3 = rows[count + 2].find_all('td')
            temp = {}
            for link in cols3[1].find_all('a', href=True):
                #This might be an issue if they have multiple files with the same name it would only save one, maybe ill look into this later
                temp[link.get_text()] = link['href']
            images.append(temp)

        count = count + 1        

    result = pd.DataFrame(
            {'filling_date': filling_dates,
             'description': descriptions,
             'name' : names,
             'monetary': monetaries,
             'entry' : entries,
             'image' : images
            })

    return result

def scrapeCaseParties(table):
    rows = table.find_all("tr")

    seqs = []
    assocs = []
    end_dates = []
    types = []
    ids = []
    names = []
    alliases = []

    count = 0

    #Scrape case parties
    for row in rows:
        if (row.has_attr('valign')):
            if (not row.has_attr('align')):
                cols1 = row.find_all('td')               
                seqs.append(cols1[0].get_text())
                assocs.append(cols1[1].get_text())
                end_dates.append(cols1[2].get_text())
                types.append(cols1[3].get_text())
                ids.append(cols1[4].get_text())
                names.append(cols1[5].get_text())

                cols2 = rows[count + 1].find_all('td')
                alliases.append(cols2[4].get_text().strip('\n'))

        count = count + 1        

    result = pd.DataFrame(
            {'seq': seqs,
             'assoc': assocs,
             'end_date' : end_dates,
             'type': types,
             'id' : ids,
             'name' : names,
             'alliase': alliases
            })

    return result

def chompString(block, f, b):
    front = block.find(f)
    back = block.find(b)
    return ((block[(front + len(f)):back]).strip()).rstrip()

def chompStringV(block, f, b):
    front = block.find(f)
    back = block.find(b)
    return ((block[(front + len(f) + 1):back]).strip()).rstrip().replace("&nbsp", "").replace('\n', ' ')

def chompStringEnd(block, f):
    front = block.find(f)
    back = block.find(";")
    return ((block[(front + len(f)):back + 4]).strip()).rstrip()

def scrapeSentences(page):
    #get sentances block and convert to raw string
    block = page.find("a", {"name": "sentences"}).text

    names = []
    sentences = []
    sequences = []
    lengths = []
    suspended_lengths = []
    consecutives = []
    concurrents = []
    serveds = []
    signeds = []
    starts = []
    probations = []
    completions = []
    sentence_details = []
    violation_nos = []

    while block.find('Name:') != -1:
        names.append(chompString(block, 'Name:','Sentence:'))
        sentences.append(chompString(block, 'Sentence:','Sequence:'))
        sequences.append(chompString(block, 'Sequence:','Length:'))
        lengths.append(chompString(block, 'Length:','Suspended Length:'))
        suspended_lengths.append(chompString(block, 'Suspended Length:','Consecutive:'))
        consecutives.append(chompString(block, 'Consecutive:','Concurrent:'))
        concurrents.append(chompString(block, 'Concurrent:','Served:'))
        serveds.append(chompString(block, 'Served:','Signed:'))
        signeds.append(chompString(block, 'Signed:','Start:'))
        starts.append(chompString(block, 'Start:','Probation:'))
        probations.append(chompString(block, 'Probation:','Completion:'))
        completions.append(chompString(block, 'Completion:','Sentence Detail:'))
        sentence_details.append(chompString(block, 'Sentence Detail:','Violation(s)'))
        violation_nos.append(chompStringEnd(block, 'Violation No:'))
        block = block[block.find(";") + 3:]


    result = pd.DataFrame(
            {'name': names,
             'sentence': sentences,
             'sequence' : sequences,
             'length': lengths,
             'suspended_length' : suspended_lengths,
             'consecutive' : consecutives,
             'concurrent': concurrents,
             'served' : serveds,
             'signed' : signeds,
             'start' : starts,
             'probation' : probations,
             'completion' : completions,
             'sentence_detail' : sentence_details,
             'violation_no' : violation_nos
            })


    return result

def scrapeViolations(page):
    #get sentances block and convert to raw string
    block = page.find("a", {"name": "violations"}).text

    violations = []
    citation_nums = []
    age_at_violations = []
    pleas = []
    disps = []
    levels = []
    violation_dates = []
   # violation_times = []
    #violation_texts = []
    

    block = block[block.find("Violation") + 9:]

    while block.find('Violation') != -1:

        violations.append(chompStringV(block, 'Violation','Citation#'))
        citation_nums.append(chompStringV(block, 'Citation#','Age at Violation'))
        age_at_violations.append(chompStringV(block, 'Age at Violation','Plea'))
        pleas.append(chompStringV(block, 'Plea','Disp'))
        disps.append(chompStringV(block, 'Disp','Level'))
        levels.append(chompStringV(block, 'Level', "Violation Date"))
        violation_dates.append(chompStringV(block, 'Violation Date','Violation Time'))
        block = block[block.find("Violation Time:") + 20:]
        #violation_times.append(chompStringV(block, 'Violation Time','\n'))
        # print(block[0:200])
        # if (block[0:200].find("Violation Text") == -1):
        #     violation_texts.append("")
        #     block = block[block.find("Violation Time") + 14:]
        # else:
        #     violation_texts.append(chompStringV(block, 'Violation Text', '\n'))
        #     block = block[block.find("Violation Text:") + 20:]


    result = pd.DataFrame(
            {'violation': violations,
             'citation_num': citation_nums,
             'age_at_violations' : age_at_violations,
             'plea': pleas,
             'disp' : disps,
             'level' : levels,
             'violation_date' : violation_dates,
             #'violation_times': violation_times,
             #'violation_text': violation_texts
            })


    return result

def getCaseData(id):
    page = getCase(id)

    table = page.find_all("table")
    if (table):

        sentences = scrapeSentences(page)

        violations = scrapeViolations(page)

        docket_entries = scrapeDocketEntries(table[3])

        case_parties = scrapeCaseParties(table[2])

        case = pd.DataFrame(
            {'sentance': [sentences],
             'violation': [violations],
             'docket_entrie' : [docket_entries],
             'case_partie': [case_parties],
            })

        print(case)

        case.to_csv("case_test.csv", sep=',')

        return case
    
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

#getAllData()
getCaseData("04CR-17-237")


#case_type
#cort_code
#docket_code