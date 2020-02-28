#!/usr/bin/env python
from bs4 import BeautifulSoup
import urllib.request, urllib.error, urllib.parse
import sys
import csv
from datetime import datetime
import re
from collections import OrderedDict
from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
MAX_ITEMS = 0
# DIVIDE IN EQUAL PARTS TO SCRAPE

def main():  
    print();
    print("This is " + sys.argv[0] + " by Ruiliang Gao. \nScrape tripadvisor")
    print("--------------------------------------------------")
    global itemCount
    itemCount = 0        
    global fileName
    fileName = "tripadvisor_" + datetime.now().strftime('%Y%m%d_%H%M') + ".csv"
    global titleList
    titleList = []
    global writer
    fw = open(fileName, "w", newline='', encoding="utf-8")
    writer = csv.writer(fw, delimiter=',', quoting=csv.QUOTE_MINIMAL)    
    writer.writerow(['date','title', 'text', 'rating','location'])   
    print("The output CSV file is: %s " % (fileName))
    print("---------------------------------------------------------")

    #central park
    # nextLink = "http://www.tripadvisor.com/Attraction_Review-g60763-d105127-Reviews-Central_Park-New_York_City_New_York.html"
    
    #brooklyn
    # nextLink = "https://www.tripadvisor.com/Attraction_Review-g60827-d2322216-Reviews-Brooklyn_Bridge_Park-Brooklyn_New_York.html"

    #new orleans
    # nextLink = "https://www.tripadvisor.com/Attraction_Review-g60864-d108045-Reviews-New_Orleans_City_Park-New_Orleans_Louisiana.html"
    
    # High Line
    startLink = "https://www.tripadvisor.com/Attraction_Review-g60763-d519474-Reviews-The_High_Line-New_York_City_New_York.html"

    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.get(startLink)
    # button = driver.find_elements_by_xpath("//spn[contains(@class,'location-review-review-list-parts-ExpandableReview')]")[0]
    # button = driver.find_elements_by_class_name("location-review-review-list-parts-ExpandableReview__cta--2mR2g")[0]
    ignored_exceptions=(NoSuchElementException,StaleElementReferenceException)
    try:
        driver.implicitly_wait(2) 
        button = WebDriverWait(driver, 20, ignored_exceptions=ignored_exceptions).until(findReadmore)
        button.click()
    except exceptions.StaleElementReferenceException as e:
        print(e)
        pass
    # span location-review-review-list-parts-ExpandableReview__cta--2mR2g
    # wait 1 sec...
    iteration = 0
    totalNumPages = 10
    analyzeIndexPage(driver)
    # https://www.tripadvisor.com/Attraction_Review-g60763-d105127-Reviews-or74755-Central_Park-New_York_City_New_York.html#REVIEWS
    # finalLink = "https://www.tripadvisor.com/Attraction_Review-g60763-d105127-Reviews-or15-Central_Park-New_York_City_New_York.html#REVIEWS"
    # finalLink = "https://www.tripadvisor.com/Attraction_Review-g60827-d2322216-Reviews-or15-Brooklyn_Bridge_Park-Brooklyn_New_York.html#REVIEWS"
    while startLink != None and iteration < totalNumPages:
        iteration = iteration+1
        # nextLink = "https://www.tripadvisor.com/Attraction_Review-g60827-d2322216-Reviews-or"+str(5*iteration)+"-Brooklyn_Bridge_Park-Brooklyn_New_York.html#REVIEWS"
        # nextLink = "https://www.tripadvisor.com/Attraction_Review-g60763-d105127-Reviews-or" + str(5*iteration) + "-Central_Park-New_York_City_New_York.html#REVIEWS"
        driver.implicitly_wait(3) 
        for i in range(4):
            try:
                driver.implicitly_wait(1) 
                Next = WebDriverWait(driver, 20, ignored_exceptions=ignored_exceptions).until(findNext)
                Next.click()
                break
            except exceptions.StaleElementReferenceException as e:
                print(e)
                pass
        # driver.get(nextLink)
        
        # button = driver.find_elements_by_xpath("//span[contains(@class,'location-review-review-list-parts-ExpandableReview')]")[0]
        for i in range(4):
            try:
                # button = driver.find_elements_by_xpath("//span[contains(@class,'location-review-review-list-parts-ExpandableReview')]")[0]
                driver.implicitly_wait(2) 
                button = WebDriverWait(driver, 20, ignored_exceptions=ignored_exceptions).until(findReadmore)
                button.click()
                break
            except exceptions.StaleElementReferenceException as e:
                print(e)
                pass
        
        analyzeIndexPage(driver)
        print("iter %s finished..." % (str(iteration)))

def findReadmore(driver):
    # element = driver.find_elements_by_xpath("//span[contains(@class,'location-review-review-list-parts-ExpandableReview')]")[0]
    element = driver.find_elements_by_xpath("//span[starts-with(@class,'location-review-review-list-parts-ExpandableReview__cta--2mR2g')]")
    if element:
        print('found button readmore')
        return element[0]
    else:
        return False

def findNext(driver):
    # element = driver.find_elements_by_xpath("//span[contains(@class,'location-review-review-list-parts-ExpandableReview')]")[0]
    element = driver.find_elements_by_xpath("//a[@class='ui_button nav next primary ']")[0]
    if element:
        print('found button Next')
        return element
    else:
        return False        

# content: location-review-review-list-parts-ExpandableReview__reviewText, location-review-review-list-parts-ExpandableReview__reviewText--gOmRC
# title : location-review-review-list-parts-ReviewTitle__reviewTitleText
# location : span class default social-member-common-MemberHometown__hometown--3kM9S small
# ratings : span class ui_bubble_rating bubble_40
# whole section : div location-review-card-Card__ui_card--2Mri0 location-review-card-Card__card--o3LVm location-review-card-Card__section--NiAcw
def analyzeIndexPage(driver):
    print("analyzeIndexPage... ")
    # host = urllib.parse.urlparse(url).netloc
    # soup = BeautifulSoup(urllib.request.urlopen(url))
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    listReviews = []
    listTitles = []
    listLocations = []
    listRatings = []
    listExpDates = []
    for section in soup.find_all("div", attrs={"class" : re.compile(r"^location-review-card-Card__ui_card.*")}):
        review = section.find("q", attrs={"class" : re.compile(r"^location-review-review-list-parts-ExpandableReview__reviewText.*")})
        content = review.findChildren("span")[0].get_text()
        if content != None:
            listReviews.append(content)
        else:
            listReviews.append("")
        
        title = section.find("a", attrs={"class" : re.compile(r"^location-review-review-list-parts-ReviewTitle__reviewTitleText.*")})
        text = title.findChildren("span")[0].get_text()
        if text != None:
            listTitles.append(text)
        else:
            listTitles.append("")
        
        rate = section.find("span", attrs={"class" : re.compile(r"^ui_bubble_rating bubble_.*")})
        if rate != None:
            listRatings.append(rate["class"][1][7:9])
        else:
            listRatings.append("")
        
        location = section.find("span",attrs={"class" : re.compile(r"^social-member-common-MemberHometown__hometown.*")})
        if location != None:
            listLocations.append(location.get_text())
        else:
            listLocations.append("")
        
        expdate = section.find("span", attrs={"class" : re.compile(r"^location-review-review-list-parts-EventDate__event_date.*")})
        if expdate != None:
            listExpDates.append(expdate.get_text()[20:])
        else:
            listExpDates.append("")
    for i in range (0,5):
        writer.writerow( (listExpDates[i], listTitles[i],  listReviews[i], listRatings[i], listLocations[i] ))
    return None

if __name__ == '__main__':
    main()#!/usr/bin/env python

