
import os
import json
import pickle
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
import multiprocessing as mp
import sys
sys.setrecursionlimit(10000) # This is pretty arbitrary...

def load_config():
    with open("./config.json",'r') as jconfig:
        master_config = json.load(jconfig)["config"]
    return master_config

# config = load_config()

class Edgar_Utils(object):
    """docstring for Edgar_Utils."""

    def __init__(self, config):
        self.config = config
        self.html_cache = self.config["directories"]["html_files"]
        self.input_dir = self.config["directories"]["inputs"]

        self.cik_filename = self.config["files"]["cik_index"]
        self.cik_path = self.input_dir + self.cik_filename

        self.url_configs = self.config["urls"]
        self.sec_url = self.url_configs["sec_url"]
        self.document_index_id = self.url_configs["document_index_id"]
        self.query_url = self.url_configs["sec_query_url"]

    def load_cik_index(self, path=None):
        if path is None:
            path = self.cik_path
        cik_frame = pd.read_csv(path)
        return dict(zip(cik_frame["Company Name"], cik_frame["CIK"]))

    def get_content_url(self, listing):

        annual_file_index_url = listing['href']
        full_doc_url = self.sec_url + annual_file_index_url

        annual_document_type = requests.get(full_doc_url)

        if annual_document_type.status_code == 200:

            annual_document_type_soup = BeautifulSoup(annual_document_type.text, 'html.parser')

            annual_doc_table = annual_document_type_soup.find_all('tr')[1] # Get the first row of the doc table
            html_doc_link = annual_doc_table.find('a')['href']

            if '.htm' in html_doc_link:
                return self.sec_url + html_doc_link

        else:
            print("Error: Unable to reach document table - Status Code", annual_document_type.status_code)

    def get_content_urls(self, cik, type='10-K'):

        results = requests.get(self.sec_url + self.query_url + '&CIK=' + cik + "&type=" + type + "&dateb=&owner=exclude&count=100")

        if results.status_code == 200:
            document_index_page = BeautifulSoup(results.text, 'html.parser')

            document_listings = document_index_page.find_all(id=self.document_index_id)

            # Parallelize
            # content_urls = [get_content_url(url) for url in document_listings]

            pool = mp.Pool(mp.cpu_count())
            content_urls = pool.map(self.get_content_url, document_listings)

            content_urls = [url for url in content_urls if url != None]

            return content_urls

        else:
            print("Error: Unable to reach the SEC.gov query URL - Status Code", results.status_code)
            return False

    # def cached_page(filename):


    # TODO - Break up URL fetching vs. cache fetching
    def fetch_content(self, url):
        content_request = requests.get(url)

        if content_request.status_code == 200:
            return content_request.text
        else:
            return False

    # def get_content(self, url_list, company_name, retry_count):
    #
    #     company_name = company_name.replace('.','') + '/'
    #
    #     cache_name = url.split('/')[-1]
    #     cached_folder = self.html_cache + company_name
    #     cached_file = self.html_cache + company_name + cache_name
    #
    #     # If we've cached the webpage, avoid making a request
    #     if os.path.exists(cached_file):
    #         with open(cached_file, 'r') as fp:
    #             content = fp.read()

    def get_content(self, url, company_name, retry_count=3):

        company_name = company_name.replace('.','') + '/'

        cache_name = url.split('/')[-1]
        cached_folder = self.html_cache + company_name
        cached_file = self.html_cache + company_name + cache_name

        # If we've cached the webpage, avoid making a request
        if os.path.exists(cached_file):
            with open(cached_file, 'r') as fp:
                content = fp.read()
        else:
            content_request = requests.get(url)

            if content_request.status_code == 200:
                content = content_request.text
            else:
                # TODO Retry N times mechanism here
                print("Error: Unable to reach the SEC.gov documents for",str(cik)," - Status Code",content_request.status_code)
                return False

            # Save to cache
            if not os.path.exists(cached_folder):
                os.mkdir(cached_folder)
            with open(cached_file,'w') as fp:
                print(content, file=fp)

        return content
