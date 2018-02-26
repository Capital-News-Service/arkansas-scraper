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

# Build URL of a search result page
def buildUrl(county, begin_date, end_date, type):
    base = "https://caseinfo.aoc.arkansas.gov/cconnect/PROD/public/ck_public_qry_doct.cp_new_case_frames"
    param_text = "?" + "county_code=" + county + "&locn_code=ALL&begin_date=" + begin_date + "&end_date=" + end_date + "&case_type=" + type
    return base + param_text

# Requests search result html data
def getSearchPage(county, begin_date, end_date, type):
    url = buildUrl(county, begin_date, end_date, type)
    #print(url)
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

# Requests individual cases html data
def getCasePage(id):
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

# Helper Method Scrapping Sentances
def chompString(block, f, b):
    front = block.find(f)
    back = block.find(b)
    return ((block[(front + len(f)):back]).strip()).rstrip()

# Helper Method Scrapping Violations
def chompStringV(block, f, b):
    front = block.find(f)
    back = block.find(b)
    return ((block[(front + len(f) + 1):back]).strip()).rstrip().replace("&nbsp", "").replace('\n', ' ')

# Helper Method Scrapping End of Sentances
def chompStringEnd(block, f):
    front = block.find(f)
    back = block.find(";")
    return ((block[(front + len(f)):back + 4]).strip()).rstrip()

# Scrape all docket entries of one case
def scrapeDocketEntries(case_id, table):
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
            {'case_id' : case_id,
             'filling_date': filling_dates,
             'description': descriptions,
             'name' : names,
             'monetary': monetaries,
             'entry' : entries,
             'image' : images
            })

    return result

# Scrape all case parties of one case
def scrapeCaseParties(case_id, table):
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
            {'case_id': case_id,
             'seq': seqs,
             'assoc': assocs,
             'end_date' : end_dates,
             'type': types,
             'id' : ids,
             'name' : names,
             'alliase': alliases
            })

    return result

# Scrape all sentances of one case
def scrapeSentences(case_id, page):
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
            {'case_id' : case_id,
             'name': names,
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

# Scrape all violations of one case
def scrapeViolations(case_id, page):
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
            {'case_id' : case_id,
             'violation': violations,
             'citation_num': citation_nums,
             'age_at_violations' : age_at_violations,
             'plea': pleas,
             'disp' : disps,
             'level' : levels,
             'violation_date' : violation_dates
            })


    return result

# Scrapes Status of an Individual Case
def scrapeStatus(case_id, table):
    rows = table.find_all("tr")

    des = []

    for row in rows:
        cols = row.find_all("td")


        for col in cols:
            des.append(col.get_text().strip())

    return des[17]

# Scrape data for each case from search result page
def getData():

    violations = []
    sentences = []
    parties = []
    docket_entries = []

    dates = []
    ids = []
    descriptions = []
    types = []
    judges = []
    courts = []

    for begin in range(2017,2018):
        end = begin + 1
        print("begin " + str(begin))
        print("end " + str(end))
        begin_date = "12/26/" + str(begin)
        end_date = "12/26/" + str(begin)

        #loop through every county
        for county in counties:
            print("county " + county)
            type = "11 - CRIMINAL CIRCUIT"

            #get search result page
            page = getSearchPage(county, begin_date, end_date, type)
            
            table = page.find("table")
            if (table):
                rows = table.find_all("tr")

                #go through each page in the table
                for row in rows:
                    cols = row.find_all("td")

                    #if its a full row
                    if (len(cols) > 5):
                        dates.append(cols[0].get_text())
                        temp_id = cols[1].get_text().split(" ", 1)[0]
                        ids.append(temp_id),
                        descriptions.append(cols[1].get_text().split(" ", 1)[1])
                        types.append(cols[2].get_text())
                        judges.append(cols[3].get_text())
                        courts.append(cols[4].get_text())

                        #get case page for indivudual case
                        temp_page = getCasePage(temp_id)
                        temp_tables = temp_page.find_all("table")
                        num = len(temp_tables)
                        if num == 6:
                            violations.append(scrapeViolations(temp_id, temp_page))
                            sentences.append(scrapeSentences(temp_id, temp_page))
                            parties.append(scrapeCaseParties(temp_id, temp_tables[3]))
                            docket_entries.append(scrapeDocketEntries(temp_id, temp_tables[4]))
                        elif num == 5:
                            violations.append(scrapeViolations(temp_id, temp_page))
                            sentences.append(scrapeSentences(temp_id, temp_page))
                            parties.append(scrapeCaseParties(temp_id, temp_tables[2]))
                            docket_entries.append(scrapeDocketEntries(temp_id, temp_tables[3]))
                        else:
                            print("Diff # of tables? # = " + num + " ID:" + temp_id)    
                        print(temp_id)
                
    cases = pd.DataFrame(
        {'date': dates,
         'id': ids,
         'description' : descriptions,
         'type': types,
         'judge' : judges,
         'court' : courts
        })

    v = pd.DataFrame(result, columns=['head', 'from', 'to', 'tweets', 'size', 'dates', 'names', 'size2', 'usernames'])
    s = pd.DataFrame(result, columns=['case_id','name','sentence','sequence','length','suspended_length','consecutive','concurrent',
             'served','signed','start','probation','completion','sentence_detail','violation_no'])
    p = pd.DataFrame(result, columns=['head', 'from', 'to', 'tweets', 'size', 'dates', 'names', 'size2', 'usernames'])
    d = pd.DataFrame(result, columns=['case_id', 'filling_date', 'description', 'name', 'monetary', 'entry', 'image'])


    print(cases)
    cases.to_csv("cases.csv", sep=',')
    violations.to_csv("violations.csv", sep=',')
    sentences.to_csv("sentences.csv", sep=',')
    parties.to_csv("parties.csv", sep=',')
    docket_entries.to_csv("docket_entries.csv", sep=',')

getData()