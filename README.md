# VMAP Web Vulnerabiliy Scanner / Penetration Testing Tool

Made by Nick (Nicholas Berridge-Argent - z5208292) for a COMP6841 Something Awesome project.

## Installation

Requirements are BeautifulSoup 4, LXML, Requests and Selenium, you can install using a venv:

```sh
python3 -m venv venv
pip3 install -r requirements.txt
chmod u+x vmap.py
```

Testing for XSS also requires Google Chrom(e|ium), and the associated Selenium web driver:

```sh
sudo apt install chromium-chromedriver
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

## GOAT Websites

A 'goat' file in malware research (coming from the idea of a sacrificial goat) is a file which is intentionally infected with malware.

For this project, GOAT is a ficticious company which we are doing security consulting for. We can use VMap to test each of their websites for a vulnerability.

There are 6 GOAT websites:

1. `goat` has a vulnerable search query, and SQLI can be used on the search bar to extract arbitrary SQL records.
2. `goat2` has a vulnerable login query, and SQLI can be used to break into an account.
3. `goat3` is identical to `goat2` - but makes a naive attempt at blacklisting SQL queries.
4. `goat4` has a 'poem selection' form which is vulnerable to LFI.
5. `goat5` is identical to `goat4` - but no longer explicitly has a form element.
6. `goat6` has a form which is vulnerable to XSS.

In addition to these, the `goat` directory also has `xss_test`, which is the useful server featured in my XSS blog post for testing the XSS vulnerability checker.

Most GOAT websites can be run just with Flask, although the SQLI ones require pyscopg2 and a local PostgreSQL installation (the schema and data files are provided).