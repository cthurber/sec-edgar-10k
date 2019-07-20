
import os
import pickle
import requests
from Statement import Statement

class Company(object):
    """Defines a company which is initiatlized with a name and identifier"""

    def __init__(self, name, config, utils, symbol=None):
        super(Company, self).__init__()
        self.name = name
        self.symbol = symbol
        self.cik = None
        # TODO this should be by year
        self.statements = []   # Array of statement objects
        self.config = config
        self.dir_config = config["directories"]
        self.utils = utils

    def get_cik(self, index):
        company_name = self.name.upper()
        if company_name in list(index.keys()):
            self.cik = index[company_name]
            return True
        else:
            return False

    def get_statements(self, processors=1):

        # TODO - Enhancement: Should make a 'producer' here that is consumed by the block below
        # TODO - Create sub-function that can handle retries
        # TODO - Handle CIK matching
        if self.cik is None:
            print("Error: CIK was not initialization for", self.name)

        # Parallelize
        # content_urls = get_content_urls(self.cik)
        # Create sub-function to fetch from cache or reach out to
        # content_urls = self.utils.get_content_urls(self.cik)
        # content = self.utils.get_content(content_urls, self.name)
        content = [self.utils.get_content(url, self.name) for url in self.utils.get_content_urls(self.cik)]

        # TODO - Enhancement: As content becomes available, this block should consume it
        for c in content:
            statement = Statement("10-K", self.config, c, processors)
            statement.get_sections() # Explicit call once statement is initialized

            statement.set_year
            self.statements.append(statement)
            # self.statements[statement.year] = statement
