import re
import json
from edgar_utils import load_config

class Statement(object):
    """Generally, this object represents a financial statement for a company
    In its current implementation however, this is pretty tightly coupled to a 10-K filing"""

    def __init__(self, type, contents):
        super(Statement, self).__init__()
        self.type = type
        self.contents = contents
        self.year = ""
        self.config_section = "statements"
        self.config = load_config()[self.config_section]

        # TODO Create Section object
        self.sections = {self.config["statement_sections"][section]["description"] : self.get_section(section) for section in self.config["statement_sections"]}

    # TODO - Critical feature... ensure a statement can be tied to a datetime
    def set_year(self):
        self.year = "2019"
        pass

    def get_section_text(self, section):

        # Gather expressions for removing HTML, spec chars, etc.
        cleaner_expressions = self.config["section_cleaners"]

        for cleaner in cleaner_expressions:
            cleaner = cleaner_expressions[cleaner]
            section = re.sub(cleaner["regex"], cleaner["replace"], section)

        return section

    def get_section(self, section):

        # Load up the title and regular expression for the requested section
        section_config = self.config["statement_sections"]
        section_exp = section_config[section]["regex"]


        # Capture the section
        # A little heavy handed, but we're confident we have only one match
        raw_section = re.finditer(section_exp, self.contents, re.MULTILINE | re.DOTALL)
        try:
            raw_section = list(raw_section)[0].group(1)

            # Clean up any special characters, HTML, etc. from the section
            section_contents = self.get_section_text(raw_section)

            return section_contents
        except:
            return ""
