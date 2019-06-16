
import os
import time # Just here for testing performance
import requests
import pickle
# import threading
import pandas as pd
from edgar_utils import load_config, load_cik_index
from Company import Company
from Statement import Statement

config = load_config()
dir_config = config["directories"]
input_config = config["inputs"]
company_cache = dir_config["companies"]

input_dir = dir_config["inputs"]

def load_company(cik):
    # Add handling for pickles not found
    company_pickle = company_cache + cik + '.pickle'
    with open(company_pickle, 'rb') as fb:
        return pickle.load(fb)

def save_company(company):
    filename = company_cache + company.cik + '.pickle'

    if not os.path.exists(filename):
        with open(filename, 'wb') as fp:
            pickle.dump(company, fp)
        return True
    else:
        return False

def load_companies(path):
    """Returns a list of company objects given an input csv"""

    company_list = []

    input_filename = path.split('/')[-1]
    try:
        path_config = input_config[input_filename]
    except:
        print("Error: Configuration not found in 'inputs' node in config.json for", path)

    company_frame = pd.read_csv(path)

    for index, company in company_frame.iterrows():
        company_name = company[path_config["company_name"]].strip('!') # May need to make a genric to strip chars out of company names that do not conform to CIK Index -- Check the errors file in the data/output directory

        # TODO Future enhancement
        # if "symbol" in list(path_config.keys())
        symbol = company[path_config["symbol"]]

        # TODO Future enhancement
        # if "cik" in list(path_config.keys())
        #     cik = path_config["cik"]

        company_list.append(Company(company_name, symbol))

    return company_list


# Loading CIK
companies = load_companies(input_dir + "NYSE.csv")
cik_index = load_cik_index()

# Capture any missed CIK matches here
missed_cik_matches = []

# Thread this?
# TODO Enhanced feature:
# - Create 'producer' that matches CIK to a company and drops the company into a global queue
# - Create 'consumer' that pops the latest company off the queue and if CIK != None, it gathers statements


single_start = time.time() # Checking performance

for company in companies:

    company_start = time.time()

    matched = company.get_cik(cik_index)

    if matched:
        # Gather statements
        company.get_statements()
        save_company(company)
        company_end = time.time()
        print(company.symbol, ", Match and fetch took,",company_end - company_start,",seconds") # Info purposes only

    elif not matched:
        missed_cik_matches.append(company.name)




with open('data/outputs/errors/missed_cik_matches.csv','w') as fp:
    missed_matches = str(missed_cik_matches).replace('[','').replace(']','').replace("'",'').replace(', ','\n')
    print(missed_matches, file=fp)

single_end = time.time() # Checking performance
cik_matching = single_end - single_start # Checking performance

print("CIK matching and statments took", cik_matchin, "seconds") # Checking performance

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

#
# with open("data/cache/corning-sample-2018-10k.html") as k:
#     contents = k.read()
#     statement = Statement('10-K', contents)
#
#     for section in statement.sections:
#         print(statement.sections[section])
