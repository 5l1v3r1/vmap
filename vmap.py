#!/usr/bin/env python3

import argparse, json, re, sys

import lfi, sqli, utils, xss

# Legally required cool hacker ASCII art
art = '''\x1B[94m
    /=======\   \\   |          / 
   //     . \\\\   +--+--~ X ~--+  
  //     .o. \\\\       LFI     |\\ 
  ||      .  ||                  
  ||  #   #  ||  # #   ###  #### 
  ||  #   #  || # # # #   # #   #
  \\\\   # #   // # # # ##### #### 
   \\\\   #   //  #   # #   # #    
    \\=======/                    
    /  /  |   \\               |  
   /  /        \\       XSS    |  
  /  /    X ~---+---~ X ~--+--+  
 /  /  SQL     /            \\    
 |--      |   /              \\   
                                 
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-#
|     VMAP Web Vuln. Tester     |
|                               |
|   Nick's COMP6841 Something   |
|        Awesome Project        |
|                               |
|         z5208292 20T1         |
#-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-#

\x1B[0m'''

print(art)

parser = argparse.ArgumentParser(description='VMAP Web Vulnerability Tester, written as Nick\'s something awesome project for COMP6841. Can test for common SQL injection and local file inclusion vulnerabilities.', epilog='Thanks for reading :)')
parser.add_argument('-l', '--login', metavar='cookie', help='test login queries, checking for the existence of a given cookie')
parser.add_argument('-f', '--flag', metavar=('flag', 'column', 'table'), nargs=3, help='test sql flag queries, checking for injecting a particular value, from a particular column, in a particular table')
parser.add_argument('-i', '--inclusion', metavar=('file', 'flag'), nargs=2, help='test for local file inclusion with the given path, file should contain the given flag')
parser.add_argument('-s', '--script', action='store_true', help='check for the ability to run user-supplied scripts')
parser.add_argument('--limit', metavar='limit', default=4, type=int, help='generalised limit for how deep searches should be (defaults to 4)')
parser.add_argument('--delay', metavar='delay', type=int, help='specify a delay between requests to avoid overloading the server')
parser.add_argument('--match-url', metavar='pattern', type=str, help='specify a regular expression which URLs must match to be considered for vulnerabilites')
parser.add_argument('--exclude-url', metavar='pattern', type=str, help='specify a regular expression for which matching URLs are not considered for vulnerabilities')
parser.add_argument('--report', metavar='file', type=str, help='output all URLs scanned, and their vulnerabilities, to the given JSON file')
parser.add_argument('target', type=str, help='the target URL')

args = parser.parse_args()

if args.flag is None and args.login is None and args.inclusion is None and args.script is None:
    print(f'Nothing to do...\nSeek not and ye shall find not\n\nUse the -h flag for help')
    sys.exit(0)

match_url = args.match_url
if match_url is not None:
    try:
        match_url = re.compile(match_url)
    except re.error:
        print('Warning: Match URL is invalid regex, treating as plain text')

exclude_url = args.exclude_url
if exclude_url is not None:
    try:
        exclude_url = re.compile(exclude_url)
    except re.error:
        print('Warning: Exclude URL is invalid regex, treating as plain text')

forms = utils.scrape(args.target, args.limit, match_url, exclude_url, args.delay)
results = []

if args.login is not None:
    print('Checking login queries...')
    results += sqli.test_login(forms, args.limit, args.delay, args.login)

if args.flag is not None:
    print('Checking flag queries...')
    results += sqli.test_flag(forms, args.limit, args.delay, args.flag[1], args.flag[2], args.flag[0])

if args.inclusion is not None:
    print('Checking local file inclusion...')
    results += lfi.test_lfi(forms, args.limit, args.delay, args.inclusion[0], args.inclusion[1])

if args.script is not None:
    print('Checking script injection...')
    results += xss.test_scripts(forms, args.limit, args.delay)

print('')

if len(results) == 0:
    print('\x1B[92mNo vulnerabilites detected, you are awesome!\x1B[0m')
else:
    for vuln in results:
        print(f'{vuln}\n')

if args.report is not None:
    report = {}
    for form in forms:
        report[form.name] = [v.json() for v in results if v.form == form]
    
    try:
        with open(args.report, 'w') as f:
            f.write(json.dumps(report))
    except Error as e:
        print(f'Could not write report: {e}')