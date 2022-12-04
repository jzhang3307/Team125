import getopt, sys
from selenium import webdriver
import pandas as pd
from datetime import datetime


def indeed_scrape(is_state, job_title):   
    driver = webdriver.Chrome('./chromedriver')

    if not is_state:
        df = pd.read_csv("./City_Template.csv")
        citi_names = df.city.tolist()
    else:
        df = pd.read_csv("./State_Template.csv")
        state_names = df.state.tolist()

    # state_names=["Alabama", "Alaska", "Arizona"]

    def get_number(inp_str):
        num = ""
        for c in inp_str:
            if c.isdigit():
                num = num + c
        if num == "":
            num = "0"
        return int(num)


    job_salary = []
 
    if is_state:
        locations = state_names
    else:
        locations = citi_names

    for location in locations:
        driver.get("https://www.indeed.com/career/salaries")

        driver.implicitly_wait(3)

        # fill search titel
        search_job = driver.find_element('xpath','//input[@id="input-title-autocomplete"]')
        search_job.clear()
        search_job.send_keys([job_title])

        # fill location
        searchLocation = driver.find_element('xpath','//input[@id="input-location-autocomplete-localized"]')
        searchLocation.clear()
        searchLocation.send_keys(location)

        # click search button
        search_button = driver.find_element('xpath','//*[@id="what-where-search-btn"]')
        search_button.click()

        driver.implicitly_wait(3)


        # get search results


        # Get exact search result amount; need try error here:
        try:
            search_salary = driver.find_element(
                'xpath',
                '//*[@data-testid="avg-salary-value"]'
                ).text
        except:
           search_salary = "0" 

        num = get_number(search_salary) 
        job_salary.append(num)
        print(location, "---",search_salary, "---", num)


    df['job_title'] = job_title 
    df['salary'] = job_salary

    if is_state:
      filename = job_title + "_salary_by_state" + ".csv" 
    else:
      filename = job_title + "_salary_by_city" + ".csv" 

    df.to_csv(datetime.now().strftime("%Y_%m_%d"+"_")+ filename, index=False)

    driver.quit()

if __name__ == "__main__":
    # Get full command-line arguments
    full_cmd_arguments = sys.argv

    # Keep all but the first
    argument_list = full_cmd_arguments[1:]

    # define the short and long options
    short_options = "hl:j:"
    long_options = ["help", "location=", "job_title="]
    
    try:
        arguments, values = getopt.getopt(argument_list, short_options, long_options)
    except getopt.error as err:
        print (str(err))
        sys.exit(2)

    is_state = True
    job_title = ""
    for current_argument, current_value in arguments:
        if current_argument in ("-h", "--help"):
            print ("python indeed_job_salary.py [--loation <state|city>] [--job_titel <title>] ")
            print ("By default the location is by states.")
            sys.exit()
        elif current_argument in ("-l", "--location"):
            print("Search location: " + current_value)
            if current_value == "city":
                is_state = False
        elif current_argument in ("-j", "--job_title"):
            print("Search job title: "+ current_value)
            job_title=current_value

    indeed_scrape(is_state, job_title)