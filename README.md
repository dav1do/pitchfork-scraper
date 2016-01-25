# pitchfork-scraper

A scraper written with scrapy with sqlalchemy/postgresql database. The staff lists scraper simply stores to a csv.

###Create or activate a Python virtual environment
You should install this project's dependencies (which is described in the next step) into a virtual environment
in order to avoid impacting the rest of your system, and to make problem solving easier.

###Install Dependencies
Install the Python packages that are needed using pip. In a terminal,
from the the project root, issue the following command:

    pip install -Ur requirements.txt

###Configure database
This is setup to use sqlalchemy and postgresql. You should be able to run cat scrape.dump | psql to create the db locally. Will probably have to create the pitchfork user (see config file for password/user info).

It could be returned to a csv by modifying settings to remove DATABASE and ITEM_PIPELINES. It'd be prudent
to remove the lines in pitchfork.spiders.reviews that connect and find the most recent review for the stop_check.
