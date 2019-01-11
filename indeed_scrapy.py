#load packages for scraping
from selenium import webdriver
from selenium.webdriver.firefox.options import Options


#load packages for data manipulation and storage
import numpy as np
import pandas as pd


import sys
import time
import argparse
from random import randint

from tqdm import tqdm


def scrape(job_title = 'data analyst', job_loc = 'california', n=500, file_name='indeed.csv', headless=True):
    start_url = 'https://www.indeed.com'
    print('initiating webdriver...')
    options = Options()
    # if headless is True:
    #     options.add_argument('--headless')
    driver = webdriver.Firefox(firefox_options = options)
    print('launch webdriver...')
    driver.get(start_url)
    time.sleep(5)

    job = driver.find_element_by_name('q')
    print(f'Job title entered: {job_title}')
    job.send_keys(job_title) # enter job title
    where = driver.find_element_by_name('l')
    time.sleep(2)
    where.clear()
    print(f'Job Location entered: {job_loc}')
    where.send_keys(job_loc) # enter location
    driver.find_element_by_tag_name('button').click() # click 'Find Jobs'
    time.sleep(5)

    job_url_set = set()
    
    print('Retrieving job urls...')
    
    while len(job_url_set) < n:
        post = driver.find_elements_by_class_name('jobsearch-SerpJobCard.row.result.clickcard')
        for p in post:
            job_url_set.add(p.find_element_by_tag_name('a').get_attribute('href'))
        time.sleep(randint(1,5))


        try:
            close = driver.find_element_by_id('popover-close-link')
            close.click()
        except:
            next_button = driver.find_elements_by_class_name('np')
            if len(next_button) == 2:
                next_button[1].click()
            else:
                next_button[0].click()

        if len(job_url_set) % 100 == 0:
            print(f'number of jobs fetched: {len(job_url_set)}')

    print(f'number of jobs fetched: {len(job_url_set)}')
    
    job_ids = []
    job_titles = []
    job_companies = []
    job_locations = []
    job_descriptions = []
    job_time_posts = []
    
    print('Retrieving job infomation...')
    for url in tqdm(job_url_set):
        driver.get(url)
        time.sleep(randint(2,10))

        job_id = driver.find_elements_by_tag_name('meta')[5].get_attribute('content').split('jk=')[1]
        job_title = driver.find_element_by_tag_name('h3').text
        company_info = driver.find_element_by_class_name('jobsearch-InlineCompanyRating.icl-u-xs-mt--xs.jobsearch-DesktopStickyContainer-companyrating').find_elements_by_tag_name('div')
        company = company_info[0].text
        location = company_info[-1].text
        jd = driver.find_element_by_class_name('jobsearch-JobComponent-description.icl-u-xs-mt--md').text
        time_post = driver.find_element_by_class_name('jobsearch-JobMetadataFooter').text.split('-')[1].strip()

        job_ids.append(job_id)
        job_titles.append(job_title)
        job_companies.append(company)
        job_locations.append(location)
        job_descriptions.append(jd)
        job_time_posts.append(time_post)

    df = pd.DataFrame()
    df['id'] = pd.Series(job_ids)
    df['title'] = pd.Series(job_titles)
    df['company'] = pd.Series(job_companies)
    df['location'] = pd.Series(job_locations)
    df['description'] = pd.Series(job_descriptions)
    df['time_posted'] = pd.Series(job_time_posts)
    
    print('Saving...')
    if file_name.endswith('.csv'):
        df.to_csv(file_name, encoding = 'utf-8', index=False)
    else:
        print('File name not proper ends with ".csv", replace with "default.csv"')
        df.to_csv('default.csv', encoding='utf-8', index=False)

    driver.close()
    print('Done')


# In[ ]:


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--job_title', '-jt', help='Enter job title', type=str, default='data analyst')
    parser.add_argument('--job_location', '-jl', help='Enter job location', type=str, default='california')
    parser.add_argument('--n', '-n', help='Enter number of jobs you want to scrape', type=int, default=25)
    parser.add_argument('--file_name', '-fn', help='Enter file name you want to store', type=str, default='indeed.csv')
    # parser.add_argument('--headless', '-hd', help='Whether run as headless', type=int, default=1)

    args = parser.parse_args()
    scrape(job_title = args.job_title,
        job_loc = args.job_location, 
        n=args.n, 
        file_name=args.file_name)
        # ,headless=args.headless)

if __name__ == '__main__':
    main()

