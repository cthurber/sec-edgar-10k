
import os
import requests
from edgar_utils import get_content, get_content_urls, load_config
from Statement import Statement

class Company(object):
    """Defines a company which is initiatlized with a name and identifier"""

    def __init__(self, name, cik):
        super(Company, self).__init__()
        self.name = name
        self.cik = cik
        # TODO this should be by year
        self.statements = []   # Array of statement objects
        self.dir_config = load_config()["directories"]

    def cache_content(self):
        # Create directory for the current date
        #
        pass

    def get_statements(self, cache=True):

        content = [get_content(url, self.name) for url in get_content_urls(self.cik)]

        for c in content:
            statement = Statement("10-K", c)
            statement.set_year()
            self.statements[statement.year] = statement

    def save(self):
        company_cache = self.dir_config["companies"]
        pass

c = Company("Corning Inc.", "0000024741")
c.get_statements()
# print(c.statements[2].sections["Management Discussion and Analysis of Financial Condition and Results of Operations"])
