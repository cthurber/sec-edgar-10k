
import os
import time # Just here for testing performance
import requests
import pickle
# import threading
import pandas as pd
from edgar_utils import load_config, load_cik_index
from Company import Company
from Statement import Statement

import multiprocessing as mp

class Worker(object):
    """docstring for Worker."""

    def __init__(self, config, company_list_file):
        super(Worker, self).__init__()
        self.config = config
        self.cik_index = load_cik_index()
        self.company_cache = config["directories"]["companies"]
        self.input_filepath = company_list_file
        # self.input_filename = company_list_file.split('/')[-1]
        self.input_config = config["inputs"][self.input_filepath.split('/')[-1]]
        self.companies = []
        self.missed_cik_matches = []

        self.processor_count = mp.cpu_count()

    def print_cik_misses(self, list, path):
        with open(path,'w') as fp:
            missed_matches = str(list).replace('[','').replace(']','').replace("'",'').replace(', ','\n')
            print(missed_matches, file=fp)

    def save_company(self, company):
        filename = self.company_cache + company.cik + '.pickle'

        if not os.path.exists(filename):
            with open(filename, 'wb') as fp:
                pickle.dump(company, fp)
            return True
        else:
            return False

    def load_company(self, company):
        filename = self.company_cache + company.cik + '.pickle'

        if os.path.exists(filename):
            with open(filename, 'rb') as fp:
                company = pickle.load(fp)
            return company
        else:
            return False

    def open_company_file(self):
        """File handler to return a dataframe given an input_filename"""
        company_frame = pd.read_csv(self.input_filepath)
        return company_frame

    def create_company(self, company_listing):
        """Returns a company object given a company name and input file"""

        # TODO - Make a genric to strip chars out of company names that do not conform to CIK Index -- Check the errors file in the data/output directory

        company_name = company_listing[self.input_config["company_name"]].strip('!')
        symbol = company_listing[self.input_config["symbol"]]

        # Create a skeleton company object
        company = Company(company_name, self.config, symbol)

        # Check if there is a valid CIK for this company
        matched = company.get_cik(self.cik_index)

        # If we have a valid CIK, fetch the statements and save the company
        if matched:

            # Check if this company has been cached locally
            cached_company = self.load_company(company)

            if cached_company:
                return cached_company

            else:
                # Gather statements
                company.get_statements()
                self.save_company(company)

        # If the CIK didn't match, we should log this to resolve later
        elif not matched:
            self.missed_cik_matches.append(company.name)

        return company

    def fetch_companies(self):
        """Populates the worker's companies list"""

        company_frame = self.open_company_file()
        # For each company in list
        # - create company object
        # -
        for index, company_listing in company_frame.iterrows():
            # Does the company already exist? (Add caching)
            # - Use CIK pickle matching
            # If it does not...
            company = self.create_company(company_listing)

            self.companies.append(company)

# print("Number of processors:", mp.cpu_count())

        # TODO - Make this optional when debugging
        # self.print_cik_misses(missed_cik_matches, 'data/outputs/errors/missed_cik_matches.csv')



# Quick test of saving the pickle
# TODO Abstract this away somewhere else
# TODO Integrate workload below into block above

# High-level workflow
# for company in list of companies
#  - Create a company object
#  - Get CIK for that company
#  - Get statements for that company
#   - Is there a pickle in the cache?
#   - If not, go out n get it
#   - Save company as a pickle
