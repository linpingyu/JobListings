#load packages for scraping
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
import time
import getpass

#load packages for data manipulation and storage
import numpy as np
import pandas as pd
import re
from random import randint

#store user name and password

#initialize starting url
start_url = 'https://www.linkedin.com'

#initialize driver using headless Firefox
options = Options()
# options.add_argument('--headless')
driver = webdriver.Firefox(firefox_options = options)
driver.get(start_url)

#passing username and password to login
username = driver.find_element_by_name('session_key')
session_key = input('username: ')
username.send_keys(session_key)

password = driver.find_element_by_name('session_password')
session_password = getpass.getpass('password: ')
password.send_keys(session_password)

driver.find_element_by_id('login-submit').click()

#navigate to jobs page
driver.find_element_by_id('jobs-nav-item').click()

#fill in position name and search
position_name = 'data analyst'
position_location = 'California'
time.sleep(2)
search = driver.find_element(By.XPATH,"//input[@placeholder='Search jobs']")
search.send_keys(position_name)
search = driver.find_element(By.XPATH,"//input[@placeholder='Search location']")
search.send_keys(position_location)
driver.find_element_by_class_name('jobs-search-box__submit-button.button-secondary-large-inverse').click()
time.sleep(2)
driver.find_element_by_class_name('dropdown.jobs-search-dropdown.jobs-search-dropdown--view-switcher.closed.ember-view').click()
driver.find_element_by_class_name('jobs-search-dropdown__option-icon').click()


#initialize a new set for storing job url from each page
job_url_set = set()

# #initialize a new list for avoiding duplicated job entries
url_test = []

# #wait for page loading
try:
	element = WebDriverWait(driver, 10).until(
		EC.presence_of_element_located(
			(By.XPATH, 
				"//a[@data-control-name='A_jobssearch_job_result_click']")))
finally:
	#execute loop to collect job urls from each page
	while len(job_url_set) < 1500:
		#scrolling down the page to load all data
		time.sleep(randint(1,3))
		driver.execute_script("window.scroll(0, 1080);")
		time.sleep(randint(1,3))
		driver.execute_script("window.scroll(1080, 2160);")
		time.sleep(randint(1,3))
		driver.execute_script("window.scroll(2160, 3240);")
		time.sleep(randint(1,3))
		driver.execute_script("window.scroll(3240, 4320);")
		

		#get page source and parse by BeautifulSoup
		source = driver.page_source
		bsObj = BeautifulSoup(source, 'lxml')

		# debug # print(bsObj.find('a',{'data-control-name':'A_jobssearch_job_result_click'}))
		for url in bsObj.find_all('a',{'data-control-name':'A_jobssearch_job_result_click'}):
			#debug # print(url.attrs['href'])
			if url.attrs['href'][0:19] not in url_test:
				job_url_set.add(url.attrs['href'])
				url_test.append(url.attrs['href'][0:19])
			else:
				next

		#monitor the number of urls collected
		print(len(job_url_set))

		#navigate to the next page
		try:
			driver.find_element(By.XPATH, "//button[@class = 'next']").click()
			time.sleep(randint(1,5))
		
		except:
			break
		


#initialize a pandas dataframe
df = pd.DataFrame()
df_full = pd.DataFrame()

job_title = []
job_company = []
job_location = []
job_industry = []
job_description = []
job_seniority = []
job_employment_type = []
job_functions = []

print('parsing...'+'\n'+'*'*20)
count = 0

for url in job_url_set:
	try:
		print('{:.2f}%'.format(count / len(job_url_set) * 100))
		count = count + 1

		driver.get(start_url+url)
		time.sleep(randint(5,10))
		driver.find_element_by_class_name('view-more-icon').click()
		# driver.find_element(By.XPATH, "//button[@class = 'view-more-icon']").click()
		
		time.sleep(randint(5,10))

		source = driver.page_source
		bsObj = BeautifulSoup(source, 'lxml')
		
		title = bsObj.find('h1').get_text()
		job_title.append(title)
		# print(job_title[-1])

		
		company = bsObj.find('h3').find('a').get_text()
		company = re.sub('[\n]*','',re.sub('^[ ]*','', company))
		job_company.append(company)
		# print(job_company[-1])
		
		location = bsObj.find('span', {'class':'jobs-details-top-card__bullet'}).get_text()
		location = re.sub('\n[ ]*', '', re.sub('^(\n[ ]*)','', location))
		job_location.append(location)
		# print(job_location[-1])


		description = bsObj.find('div', {'id':'job-details'}).get_text()
		description = re.sub('Job description','',re.sub(' [ ]+', '', re.sub('\n', '', description)))
		job_description.append(description)
		# print(job_description[-1])
		
		seniority = bsObj.find('div',{'class':'jobs-description-details'}).find_all('p')[0].get_text()
		job_seniority.append(seniority)
		# print(job_seniority[-1])
		
		employment_type = bsObj.find('div',{'class':'jobs-description-details'}).find_all('p')[1].get_text()
		job_employment_type.append(employment_type)
		# print(job_employment_type[-1])
		
		industry = bsObj.find('div',{'class':'jobs-description-details'}).find_all('ul')[0].get_text()
		industry = re.sub('^,|,$', '', re.sub(',and,|,,|,\n',',', re.sub('[\n]*[ ]+', ',', industry)))
		job_industry.append(industry)
		# print(job_industry[-1])

		function = bsObj.find('div',{'class':'jobs-description-details'}).find_all('ul')[1].get_text()
		job_functions.append(function)
		# print(job_functions[-1])
		
		time.sleep(randint(5,10))
		print(count)


		if count % 5 == 0:
			df['title'] = pd.Series(job_title)
			df['company'] = pd.Series(job_company)
			df['location'] = pd.Series(job_location)
			df['industry'] = pd.Series(job_industry)
			df['description'] = pd.Series(job_description)
			df['seniority'] = pd.Series(job_seniority)
			df['employment_type'] = pd.Series(job_employment_type)
			df['functions'] = pd.Series(job_functions)

			job_title = []
			job_company = []
			job_location = []
			job_industry = []
			job_description = []
			job_seniority = []
			job_employment_type = []
			job_functions = []

			df_full = pd.concat([df_full, df])

			print('saving...')
			print('{} lines have been retrieved.'.format(df_full.shape[0]))
			df_full.to_csv('JDs.csv', encoding = 'utf-8', index=False)

	except:
		next



#close the driver
driver.close()

df['title'] = pd.Series(job_title)
df['company'] = pd.Series(job_company)
df['location'] = pd.Series(job_location)
df['industry'] = pd.Series(job_industry)
df['description'] = pd.Series(job_description)
df['seniority'] = pd.Series(job_seniority)
df['employment_type'] = pd.Series(job_employment_type)
df['functions'] = pd.Series(job_functions)

df_full = pd.concat([df_full, df])

df_full.to_csv('Jds.csv', encoding = 'utf-8', index = False)