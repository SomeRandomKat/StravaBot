###############################
#                             #
# StravaScraper v3.1          #
# By DumbBitchClub            #
# DumbBitch.club | DumbBit.ch #
#							  #
###############################
	
from bs4 import BeautifulSoup
import requests
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time
import sqlite3
from unidecode import unidecode

class StravaScraper(object):   
    
    # Login to strava using email and password
    def login(self, driver):       
        driver.get ('https://www.strava.com/login/session')
        driver.find_element_by_id('email').send_keys('katerinatiddy@gmail.com')
        driver.find_element_by_id ('password').send_keys('veG4nABN9jzdGPL')
        driver.find_element_by_id('login-button').click()
        
    
    # Connect to databse
    def db_connection(self, database):
        conn = None
        try:
            conn = sqlite3.connect(database)
            print('Database connected...')
            print()
        except Error as e:
            print(e)

        return conn 


    # Insert values into the database if they don't already exist
    def sql_insert(conn, athlete, datetime, duration):
        c = conn.cursor()
        #c.execute('INSERT INTO data (name, date, duration) VALUES(?, ?, ?) SELECT * FROM data WHERE NOT EXISTS (SELECT * FROM data WHERE VALUES = (?, ?, ?))', (athlete, datetime, duration, athlete, datetime, duration))
        c.execute('INSERT INTO data (name, date, duration) VALUES(?, ?, ?);', (athlete, datetime, duration))
        #c.execute('INSERT INTO data (name, date, duration) VALUES (?, ?, ?) ON CONFLICT (name, date, duration) DO NOTHING;', (athlete, datetime, duration))


    # Go to club activity feed and pull data
    def data_scraper(self, driver, conn):
        c = conn.cursor()
        c.execute('SELECT MAX(date) FROM data;')
        last_date = str(c.fetchone())
        last_date = last_date.strip("(),- '")
        if(last_date == 'None'):
            last_date = 0
        else:
            last_date = int(float(last_date.replace('-', '')))
        print('Last date in db: ', last_date)

        driver.get("https://www.strava.com/clubs/774078/recent_activity")

        ScrollNumber = 10 # How many scrolls down the page to go
        for i in range(1, ScrollNumber):
            driver.execute_script("window.scrollTo(1,50000)")
            time.sleep(5)

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        activities = soup.find_all('div', {'class':['activity entity-details feed-entry',
                                                    'activity entity-details feed-entry min-view']})

        print('Inserting into database...')
        for a in activities:
            datetime = a.time['datetime']
            athlete = a.find('a', class_ = 'entry-athlete')
            duration = a.find('li', title = 'Time')

            #if None in (athlete, datetime, duration):
                #continue
            datetime = datetime[:-13]

            if(int(datetime.replace('-', '')) > last_date):
                athlete = athlete.text.strip()
                if(athlete.endswith('Subscriber')):
                    athlete = athlete[:-11]
                athlete = unidecode(athlete)
                duration = duration.text.strip()

                if duration.endswith('s'):
                    duration_s = int(duration[-3:-1])
                    duration_m = int(duration[:2])
                    duration = duration_m
                    if (duration_s >= 30):
                        duration = duration + 1
                else:
                    duration_m = int(duration[-3:-1])
                    duration_h = int(duration[:1])
                    duration = duration_m + (duration_h * 60)

                StravaScraper.sql_insert(conn, athlete, datetime, duration)
            print(athlete)
            print(datetime)
            print(duration)
            print()
        conn.commit()
        conn.close()
        print('Insert complete...')
        print()


def main():
    import sys
    print('---------------------------')
    print('StravaScraper v3.1')
    print('By DumbBitchClub')
    print('DumbBitch.club | DumbBit.ch')
    print('---------------------------')
    print()

    # Open chromedriver to open webpages
    print('Opening chromedriver...')
    #chromrdriver = "C:/Users/kater/Desktop/Strava/chromedriver"
    options = webdriver.ChromeOptions()
    options.add_argument('no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=80,80')
    options.add_argument('--disable-dev-shm-usage')
    options.set_headless()
    chromrdriver = '/home/katerina/Strava/chromedriver'
    os.environ["webdriver.chrome.driver"] = chromrdriver
    driver = webdriver.Chrome(chromrdriver, chrome_options = options)

    print('Connecting to database...')
    database = r"/home/katerina/Strava/strava.db"
    #database = r'C:/Users/kater/Desktop/Strava/strava.db'

    scraper = StravaScraper()

    conn = scraper.db_connection(database)
    c = conn.cursor()
    
    print('Logging into Strava...')
    scraper.login(driver)
    print('Logged in...')
    print()
    print('Scraping data...')
    scraper.data_scraper(driver, conn)
    
    driver.close()
    print('Connection closed.')


if __name__ == '__main__':
    main()