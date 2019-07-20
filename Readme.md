# SEC Edgar Library

## Overview

In lieu of a proper library to access and process 10-K filings 

## Usage

### Structure

A **Worker** has a list of **Company** objects that can be populated by calling the **fetch_companies()** method

A **Company** has many **Statement**s. In its current state, only 10-K statements are supported

A **Statement** has many **Section**s. These sections are defined in **config.json** by a combination of descriptions and regular expressions

A **Section** has a **content** attribute and a **name** derived from the description assigned in the **config.json** file

### Sample

The following sample shows how you can use an instance of a **Worker** class to fetch companies and their statements, iterate through the resulting list, and access the statement's content

```python
from edgar_utils import load_config
from Worker import Worker

def main():
    config = load_config()
    company_list_file = "data/inputs/NYSE.csv" # Feed in your sheet of companies
    worker = Worker(config, company_list_file)
    
    worker.fetch_companies()
    
    for company in worker.companies:
      statements = company.statements
      for statement in statements:
        print(statement.content)
```



### The road ahead

Tracking a list of todos here for the project:

- [ ] Implement retry when fetching statements
- [ ] Implement retry when fetching statement URLs for a company
- [ ] Implement throttling on statement web requests
- [ ] Implement throttling on statement URL web requests
- [ ] Implement info logging
- [ ] Multi-thread statement web requests
- [ ] Multi-thread matching of CIKs (Company IDs)