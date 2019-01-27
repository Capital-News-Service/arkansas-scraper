# Arkansas-Scraper

This code scrapes the [Arkansas CourtConnect](https://caseinfo.arcourts.gov/cconnect/PROD/public/ck_public_qry_main.cp_main_idx) website's database and gathers a dataset of all criminal cases.

Built for [Capital News Serive](https://cnsmaryland.org/home) as part of the [Trading Away Justice](https://cnsmaryland.org/interactives/spring-2018/plea-bargain/index.html) project. 

Made by Jake Gluck [jagluck.github.io](jagluck.github.io).   
jakeagluck@gmail.com jagluck@terpmail.umd.edu

# How It Works

### Technologies

The script is written in Python.

We use the library BeautifulSoup and [Selenium](https://www.seleniumhq.org/) for the scraping.

We use Pandas to collect the scraped data and turn it into CSV files. 

### Files

fields.py - A json formatted file containing the lists of every county and the types we want to search for.

ArkansasScraper.py - Python file that does the scraping.

### Overview

Here is how the code works on a high level.


```
1. Load in counties and types from fields.py.  
2. We create our searches and run them one at a time in getData(). We build the searchs first by year, than type, than county.
3. In getSearchPage we request and return one searchs results.
4. In getData() we begin the process of going through every case in the returned search.

For each case we run this process.

5. In getCasePage() we request and return the case page for that indivudual case.
6. In getData() we split the returned page into sections and send them to their own functions.
7. In scrapeViolations(), scrapeSentences(), scrapeCaseParties(), and scrapeDocketEntries() we extract information about the case and return it.
8. In getCasePage() we collect the returned data into our four data structures. One for each section type of information (Violations, Sentences, CaseParties, and DocketEntries).

9. We now repreat this process for every case in the returned search.
10. We now repeat the search process for every search.
11. After all searches we will have completed the script.
```

I recommend splitting the process into each year because it takes many hours to run and saving each year as four csvs individually.  
