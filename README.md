# VMAP Web Vulnerabiliy Scanner / Penetration Testing Tool

Made by Nick for a COMP6841 Something Awesome project.

## Installation

Requirements are BeautifulSoup 4, LXML, Requests and Selenium, you can install using a venv:

```sh
python3 -m venv venv
pip3 install -r requirements.txt
chmod u+x vmap.py
```

The easiest way to use VMAP is with the [PhantomJS](https://phantomjs.org/) headless browser, which can be installed on Ubuntu like so:

```sh
sudo apt install phantomjs
```

## Running

After installing:

```sh
. venv/bin/activate
./vmap.py -h
# other vmap commands / other commands
deactivate
```

## Features

Currently supported are level 0 and level 1 from the proposal, plus some extra convenience features:

1. Supports various kinds of SQL injection testing.
2. Locates form elements, plus any clickable URL which functions as a form.
3. Supports checking for LFI by locating a specific file.
4. Provides optional rate-limiting to avoid overloading the server / bypass any rate-limiting.
5. Provides the ability to exclude / include URLs based on regular expressions, **very** necessary when a page includes external resources.
6. Can export scraped URLs and forms and any vulnerabilities to a JSON file.

Run with the help flag `-h` for more info.
