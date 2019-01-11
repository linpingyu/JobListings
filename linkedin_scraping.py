#load packages for scraping
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
import time
import getpass
import sys

#load packages for data manipulation and storage
import numpy as np
import pandas as pd
import re
from random import randint


def scrap(n=500, file_name='df.csv'):
	#store user name and password
	session_key = input('username: ')
	session_password = getpass.getpass('password: ')

	#initialize starting url
	start_url = 'https://www.linkedin.com'

	#initialize driver using headless Firefox
	options = Options()
	options.add_argument('--headless')
	driver = webdriver.Firefox(firefox_options = options)
	driver.get(start_url)

	#passing username and password to login
	username = driver.find_element_by_name('session_key')
	username.send_keys(session_key)

	password = driver.find_element_by_name('session_password')
	password.send_keys(session_password)

	driver.find_element_by_id('login-submit').click()

	#navigate to jobs page
	driver.find_element_by_id('jobs-nav-item').click()

	#fill in position name and search
	position_name = 'data analyst'

	search = driver.find_element(By.XPATH,"//input[@placeholder='Search jobs']")
	search.send_keys(position_name)
	driver.find_element_by_class_name('jobs-search-box__submit-button.button-secondary-large-inverse').click()

	# driver.find_element(By.XPATH,"//input[@placeholder='Job title, keywords, or company name']").send_keys('data analyst')
	# driver.find_element(By.XPATH,"//input[@placeholder='Location']").send_keys('')
	# driver.find_element(By.XPATH, "//button[@type = 'submit']").click()

	#initialize a new set for storing job url from each page
	job_url_set = set()

	#initialize a new list for avoiding duplicated job entries
	url_test = []

	#wait for page loading
	try:
		element = WebDriverWait(driver, 10).until(
			EC.presence_of_element_located(
				(By.XPATH, 
					"//a[@data-control-name='A_jobssearch_job_result_click']")))
	finally:
		#execute loop to collect job urls from each page
		while len(job_url_set) < n:
			#scrolling down the page to load all data
			driver.execute_script("window.scroll(0, 1080);")
			time.sleep(randint(1,5))
			driver.execute_script("window.scroll(1080, 2160);")
			time.sleep(randint(1,5))
			driver.execute_script("window.scroll(2160, 3240);")
			time.sleep(randint(1,5))
			driver.execute_script("window.scroll(3240, 4320);")
			time.sleep(randint(1,5))

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

	job_title = []
	job_company = []
	job_location = []
	job_industry = []
	job_description = []
	job_seniority = []
	job_employment_type = []
	job_functions = []

	print('parsing...'+'\n'+'*'*20)
	count = 1

	for url in job_url_set:
		print(str(count / len(job_url_set))+'%')
		count = count + 1

		driver.get(start_url+url)
		time.sleep(randint(1,5))
		driver.find_element(By.XPATH, "//button[@class = 'view-more-icon']").click()
		
		time.sleep(randint(1,5))

		source = driver.page_source
		bsObj = BeautifulSoup(source, 'lxml')
		
		title = bsObj.find('h1').get_text()
		job_title.append(title)
		
		company = bsObj.find('h3').find('a').get_text()
		job_company.append(company)
		
		location = bsObj.find('span', {'class':'jobs-details-top-card__bullet'}).get_text()
		job_location.append(location)

		description = bsObj.find('div', {'id':'job-details'}).get_text()
		job_description.append(description)
		
		seniority = bsObj.find('div',{'class':'jobs-description-details'}).find_all('p')[0].get_text()
		job_seniority.append(seniority)
		
		employment_type = bsObj.find('div',{'class':'jobs-description-details'}).find_all('p')[1].get_text()
		job_employment_type.append(employment_type)
		
		industry = bsObj.find('div',{'class':'jobs-description-details'}).find_all('ul')[0].get_text()
		job_industry.append(industry)

		function = bsObj.find('div',{'class':'jobs-description-details'}).find_all('ul')[1].get_text()
		job_functions.append(function)
		
		time.sleep(randint(1,5))

	df['title'] = pd.Series(job_title)
	df['company'] = pd.Series(job_company)
	df['location'] = pd.Series(job_location)
	df['industry'] = pd.Series(job_industry)
	df['description'] = pd.Series(job_description)
	df['seniority'] = pd.Series(job_seniority)
	df['employment_type'] = pd.Series(job_employment_type)
	df['functions'] = pd.Series(job_functions)

	#initial parsing for text data
	df.company = df.company.apply(lambda x: re.sub('[\n]*','',re.sub('^[ ]*','', x)))
	df.location = df.location.apply(lambda x: re.sub('\n[ ]*', '', re.sub('^(\n.*\n[ ]*)','', x)))
	df.industry = df.industry.apply(lambda x: re.sub('^,','', re.sub('\n', ',', x)))
	df.description = df.description.apply(lambda x: re.sub('( [ ]+)', '', x))
	df.functions = df.functions.apply(lambda x: re.sub('\n', '', x))


	df.to_csv(file_name, encoding = 'utf-8')

	#close the driver
	driver.close()


def main():
	n, file_name = sys.argv[1:]
	scrap(n, file_name)

if __name__ == '__main__':
	main()