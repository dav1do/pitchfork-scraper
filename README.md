# pitchfork-scraper

A scraper written with scrapy with sqlalchemy/postgresql database. The staff lists scraper simply stores to a csv.

This **most certainly** doesn't work anymore, as I haven't touched it in years and the pitchfork UI is completely different. It was really just a chance to play around with query selectors, python and postgresql for the first time (which is painfully obvious in hindsight).

## Getting started

### Create or activate a Python virtual environment

Use mkvritualenv e.g. `mkvirtualenvvenv -p python3`. next time you can `workon venv`

### Install Dependencies

Install the Python packages that are needed using pip. In a terminal,
from the the project root, issue the following command:

    pip install -r requirements.txt

### Configure database

This is setup to use sqlalchemy and postgresql. You should be able to run cat scrape.dump | psql to create the db locally (I had to use sudo -u postgres bash and then cat scrape.dump | psql on my centOS VM). Will also have to create the pitchfork user and then add the user/password to the config file.

It could be returned to a csv by modifying settings to remove DATABASE and ITEM_PIPELINES. It'd be prudent
to remove the lines in pitchfork.spiders.reviews that connect and find the most recent review for the stop_check.
