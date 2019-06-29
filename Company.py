
import os
import pickle
import requests
from edgar_utils import get_content, get_content_urls, load_config
from Statement import Statement

class Company(object):
    """Defines a company which is initiatlized with a name and identifier"""

    def __init__(self, name, config, symbol=None):
        super(Company, self).__init__()
        self.name = name
        self.symbol = symbol
        self.cik = None
        # TODO this should be by year
        self.statements = []   # Array of statement objects
        self.config = config
        self.dir_config = config["directories"]

    def cache_content(self):
        # Create directory for the current date
        #
        pass

    def get_cik(self, index):
        company_name = self.name.upper()
        if company_name in list(index.keys()):
            self.cik = index[company_name]
            return True
        else:
            return False

    def get_statements(self, cache=True):

        # TODO - Enhancement: Should make a 'producer' here that is consumed by the block below
        # TODO - Create sub-function that can handle retries
        # TODO - Handle CIK matching
        if self.cik is None:
            print("Error: CIK was not initialization for", self.name)

        content = [get_content(url, self.name) for url in get_content_urls(self.cik)]

        # TODO - Enhancement: As content becomes available, this block should consume it
        for c in content:
            statement = Statement("10-K", self.config, c)
            statement.set_year
            self.statements.append(statement)
            # self.statements[statement.year] = statement

    def save(self):
        pass
