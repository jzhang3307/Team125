import getopt, sys
from selenium import webdriver
import pandas as pd
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import time


def indeed_scrape(is_state, field, key_word):   
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome('./chromedriver', chrome_options=options)

    if not is_state:
        df = pd.read_csv("./City_Template.csv")
        citi_names = df.city.tolist()
    else:
        df = pd.read_csv("./State_Template.csv")
        state_names = df.state.tolist()


    # state_names=["Rhode Island","Alabama", "Alaska", "Arizona"]

    def get_count(inp_str):
        num = ""
        for c in inp_str:
            if c.isdigit():
                num = num + c
        if num == "":
            num = "0"
        return int(num)

    def clean_str(str):
        str = ''.join(ch for ch in str if ch.isalnum())
        str = str.replace('Page1','')
        return str

    job_counts = []
    web_response = []

    if is_state:
        locations = state_names
    else:
        locations = citi_names

    for location in locations:
        driver.get("https://www.indeed.com/advanced_search")

        driver.implicitly_wait(3)

        # search analyst, With all of these words
        search_job = driver.find_element('xpath','//input[@id="as_and"]')
        search_job.send_keys([field])

        # add key words, such as entry level 
        if key_word != '':
            search_keyword = driver.find_element('xpath','//input[@id="as_phr"]')
            search_keyword.send_keys([key_word])

        # search location
        searchLocation = driver.find_element('xpath','//input[@id="where"]')
        searchLocation.clear()
        searchLocation.send_keys(location)

        # limited to all the time
        result_age = driver.find_element(
            'xpath',
            '//select[@id="fromage"]//option[@value="any"]')
        result_age.click()

        # location: only in
        result_age = driver.find_element(
            'xpath',
            '//select[@id="radius"]//option[@value="0"]')
        result_age.click()

        driver.implicitly_wait(3)

        # push search button
        search_button = driver.find_element('xpath','//*[@id="fj"]')
        search_button.click()
        driver.implicitly_wait(10)

        # Get exact search result amount; need try error here:

        try:
            search_count = driver.find_element(
                'xpath',
                "//div[contains(@class,'jobsearch-JobCountAndSortPane-jobCount')]"
                ).text
        except:
           search_count = "0jobs" 

        search_count = clean_str(search_count) 
        num = get_count(search_count) # needs revision to get number; save the original value
        job_counts.append(num)
        print(location, "---",search_count, "---", num)

        web_response.append(search_count.rstrip('\r\n'))
        time.sleep(5)

 

    # df['location'] = locations
    # df['html_text'] = web_response
    df['job_title'] = field 
    df['skill'] = key_word 
    df['count'] = job_counts
    # add pupulation and coordinates here if the location is city

    if is_state:
      filename = field + "_by_state_" + key_word + ".csv" 
    else:
      filename = field + "_by_city_" + key_word + ".csv" 

    df.to_csv(datetime.now().strftime("%Y_%m_%d"+"_")+ filename, index=False)

    driver.quit()

if __name__ == "__main__":
    # Get full command-line arguments
    full_cmd_arguments = sys.argv

    # Keep all but the first
    argument_list = full_cmd_arguments[1:]

    # define the short and long options
    short_options = "hl:f:s:"
    long_options = ["help", "location=", "field=", "skill="]
    
    try:
        arguments, values = getopt.getopt(argument_list, short_options, long_options)
    except getopt.error as err:
        print (str(err))
        sys.exit(2)

    is_state = True
    field = "analytics"
    skill = ""
    for current_argument, current_value in arguments:
        if current_argument in ("-h", "--help"):
            print ("python indeed_job_count.py [--loation <state|city>] [--field <field>] [--skill <skill>]")
            print ("By default the field is analytics, the skill is empty, and the location is states.")
            sys.exit()
        elif current_argument in ("-l", "--location"):
            print("Search location: " + current_value)
            if current_value == "city":
                is_state = False
        elif current_argument in ("-f", "--field"):
            print("Search field: "+ current_value)
            field=current_value
        elif current_argument in ("-s", "--skill"):
            print ("Search skill: " + current_value)
            skill=current_value

    indeed_scrape(is_state, field, skill)