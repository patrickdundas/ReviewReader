#
# Software by Patrick Dundas, All rights reserved.
# Original scripting, 7/20/2018
# Scrape Amazon for review data for later analysis
#
# check for library data file
# if data file, check for unscraped pages
# once all unscraped are used, fill library data file with new pages
#

import requests
from time import sleep
from lxml import html
from datetime import datetime


def main():
    global indexes
    global debug
    global allowedLinks
    global completions
    global already_indexed
    global max_char_print

    startTime = datetime.now()

    allowedLinks = ['https://amazon.com','https://www.amazon.com','http://www.amazon.com','http://amazon.com']
    indexes = read_index_file()
    completions = read_completion_file()
    debug = False
    starting_link_orig = "https://www.amazon.com/gp/site-directory/ref=nav_shopall_fullstore"
    max_links = 500000
    already_indexed = []
    indexes = []

    if debug:
        max_char_print = 1000
    else:
        max_char_print = 40

    print "Amazon Review Scraper is Starting Up.."

    # print "Looking for product index file"


    # if indexes:
    #     for page in indexes:
    #         if page not in completions:
    #             scrape_for_reviews(page)
    #             completions.append(page)
    #             indexes.remove(page)
    #         else:
    #             indexes.remove(page)
    # else:
    #     indexes = []


    if completions:
        print completions
    else:
        completions = []

    find_reviews("https://www.amazon.com/gp/product/B075SGF3V3/")
    print "Starting Indexing"


    #if there are no indexed links
    if len(indexes) < 1:
        grow_index(starting_link_orig)
        print "Initial index growth completed, ready to start indexing at depth 0"
        print indexes

        # sleep(10)



    for index in indexes:
        print "Starting growth on link "+index[0:max_char_print]
        grow_index(index)
        if len(indexes) > max_links:
            print " \n\n\n------------ INDEXING COMPLETE [LIMIT "+str(max_links)+"] ------------ "
            print "Indexing chunk complete. "+str(len(indexes))+" links found total. "+str(len(already_indexed))+" pages checked for links"
            print " ------------ -------------------------------------------- ------------ \n\n\n"
            break

    indexing_duration = datetime.now() - startTime
    print "done indexing. Took "+str(indexing_duration)+" to find "+str(len(indexes))+" links and index "+str(len(already_indexed))+" pages."

    #start searching found pages for reviews

def find_reviews(page_link):
    global indexes
    global debug
    global completions
    global max_char_print

    found_reviews_on_page = 0

    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}

    page = requests.get(page_link,headers = headers,verify=True)

    page_response = page.text

    parser = html.fromstring(page_response)

    XPATH_LINKS  = "/html/body//a[contains(@data-hook,'see-all-reviews-link-foot')]/@href"
    raw_links = parser.xpath(XPATH_LINKS)

    if debug:
        print raw_links

    try:
        if raw_links[0]:
            print 'Found a review link!'

            #now go to the reviews link and read the reviews
            page = requests.get("https://www.amazon.com"+raw_links[0],headers = headers,verify=True)

            page_response = page.text

            parser = html.fromstring(page_response)

            XPATH_REVIEW_TITLES  = "/html/body//a[@data-hook='review-title']/text()"

            raw_titles = parser.xpath(XPATH_REVIEW_TITLES)

            print(raw_titles)
            sleep(10)

    except IndexError:
        print 'No review link found on this page'

    sleep(10)

    #for each new amazon link on page
    for link in raw_links:
        #if link has not been indexed yet
        if link not in already_indexed:
            #if an amazon link
            if any(ext in link for ext in allowedLinks) or link[0:1] is "/" and "redirect" not in link:

                #if its a relative link, add the domain to the beginning
                if link[0:1] is "/":
                    link = "https://www.amazon.com" + link

                #save the link for scraping later
                found_links_on_page += 1
                indexes.append(link)
                if debug:
                    print "[Added Index] "+link[0:max_char_print]
            #if not an amazon link, skip
            else:
                if debug:
                    print "[DEBUG][Not Allowed] "+link[0:max_char_print]
        #if link already indexed, skip
        else:
            if debug:
                print "[DEBUG][Skipped Index] "+link[0:max_char_print]

    #mark the current page as indexed
    already_indexed.append(page_link)

    #show quick report
    print "Finished scraping links from "+page_link[0:max_char_print]
    print "Found: "+str(found_links_on_page)+" usable links on this page"
    print "Total: " + str(len(indexes)) + " total usable links"
    print " ------------ -------------------------------- ------------ "



#find all links on a page and add them to indexes
def grow_index(page_link):

    global indexes
    global debug
    global allowedLinks
    global completions
    global already_indexed
    global max_char_print

    found_links_on_page = 0

    headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}

    page = requests.get(page_link,headers = headers,verify=True)

    page_response = page.text

    parser = html.fromstring(page_response)

    XPATH_LINKS  = '/html/body//a/@href'
    raw_links = parser.xpath(XPATH_LINKS)

    if debug:
        print raw_links

    #for each new amazon link on page
    for link in raw_links:
        #if link has not been indexed yet
        if link not in already_indexed:
            #if an amazon link
            if any(ext in link for ext in allowedLinks) or link[0:1] is "/" and "redirect" not in link:

                #if its a relative link, add the domain to the beginning
                if link[0:1] is "/":
                    link = "https://www.amazon.com" + link

                #save the link for scraping later
                found_links_on_page += 1
                indexes.append(link)
                if debug:
                    print "[Added Index] "+link[0:max_char_print]
            #if not an amazon link, skip
            else:
                if debug:
                    print "[DEBUG][Not Allowed] "+link[0:max_char_print]
        #if link already indexed, skip
        else:
            if debug:
                print "[DEBUG][Skipped Index] "+link[0:max_char_print]

    #mark the current page as indexed
    already_indexed.append(page_link)

    #show quick report
    print "Finished scraping links from "+page_link[0:max_char_print]
    print "Found: "+str(found_links_on_page)+" usable links on this page"
    print "Total: " + str(len(indexes)) + " total usable links"
    print " ------------ -------------------------------- ------------ "


def read_index_file():
    try:
        libfile = open("indexfile.txt", "r")

        count = 0
        indexes = []

        for line in libfile:
            count += 1
            indexes.append(line.strip())

        print "Found "+str(count)+" saved indexes"
        if count > 0:
            return indexes
        else:
            return False

    except Exception as e:
        print "An error occurred, assuming no index file." + str(e)
        return False

def read_completion_file():
    try:
        libfile = open("completionfile.txt", "r")

        count = 0
        indexes = []

        for line in libfile:
            count += 1
            indexes.append(line.strip())

        print "Found "+str(count)+" completed indexes"
        if count > 0:
            return indexes
        else:
            return False

    except Exception as e:
        print "An error occurred, assuming no completion file." + str(e)
        return False


main()
