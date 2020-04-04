import bs4, random, requests, re, time, typing

SoupifyResult = typing.Union[typing.Tuple[None, int, None], typing.Tuple[bs4.BeautifulSoup, None, typing.Optional[str]]]
SouplessResult = typing.Union[typing.Tuple[None, int], typing.Tuple[str, None]]

'''
Represents a HTML form
'''
class Form():
    def __init__(self, url: str, method: str, ftype: str = 'form') -> None:
        self._url = url
        self._method = method
        self._type = ftype
        self._fields = []
    
    @property
    def name(self) -> str:
        return self._method + ' ' + self._url + ' (' + self._type + ')'

    def add_field(self, name: str) -> None:
        self._fields.append(name)

    def get_fields(self) -> typing.List[str]:
        return self._fields

    def request(self, values: typing.Dict[str, str], cookie: typing.Optional[str]) -> SoupifyResult:
        return soupify(self._url, self._method, values, cookie)
    
    def soupless_request(self, values: typing.Dict[str, str]) -> SouplessResult:
        return soupless(self._url, self._method, values)

    def __repr__(self) -> str:
        return f'{self._type} {self._method} {self._url} (' + ', '.join(self._fields) + ')'

'''
Make a request to a URL and turn it into beautiful soup
'''
def soupify(url: str, method: str = 'GET', payload: typing.Dict[str, str] = {}, cookie: typing.Optional[str] = None) -> SoupifyResult:
    s = requests.Session()

    if method == 'GET':
        res = s.get(url, params=payload)
        if not res.ok:
            return None, res.status_code, None
        return bs4.BeautifulSoup(res.text, 'lxml'), None, s.cookies[cookie] if (cookie is not None and cookie in s.cookies) else None
    elif method == 'POST':
        res = s.post(url, data=payload)
        if not res.ok:
            return None, res.status_code, None
        return bs4.BeautifulSoup(res.text, 'lxml'), None, s.cookies[cookie] if (cookie is not None and cookie in s.cookies) else None

'''
Make a request to a URL and then return the URL for the final page, useful for JS
'''
def soupless(url: str, method: str = 'GET', payload: typing.Dict[str, str] = {}) -> SouplessResult:
    s = requests.Session()

    if method == 'GET':
        res = s.get(url, params=payload)
        if not res.ok:
            return None, res.status_code
        return res.url, None
    elif method == 'POST':
        res = s.post(url, data=payload)
        if not res.ok:
            return None, res.status_code
        return res.url, None

'''
Scrape a website to find all forms and form-like URLs
'''
def scrape(start_url: str, limit: int, match_url: typing.Union[str, re.Pattern, None], exclude_url: typing.Union[str, re.Pattern, None], delay: typing.Optional[int]) -> typing.List[Form]:
    queue = []
    results = []
    visited = set()

    queue.append((start_url, limit))

    while len(queue) > 0:
        this_url, depth = queue.pop(0)
        visited.add(this_url)

        base = this_url.split('/')[0] + '//' + this_url.split('/')[2] + '/'

        if depth == 0:
            print(f'Warning: Not scanning {this_url} due to limits')
            continue

        if delay is not None:
            time.sleep(delay)

        page, err, _ = soupify(this_url)

        results += find_formlike(this_url, match_url, exclude_url)
        results += find_forms(this_url, match_url, exclude_url)

        for link in page.find_all('a'):
            next_url = link.get('href')

            if next_url is None:
                continue

            if re.search(r'^(https?:)?//', next_url):
                pass
            elif not next_url.startswith('/'):
                next_url = this_url + '/' + next_url
            else:
                next_url = base + next_url[1:]

            if match_url is not None and not re.search(match_url, next_url):
                continue

            if exclude_url is not None and re.search(exclude_url, next_url):
                continue

            if next_url in visited:
                continue

            queue.append((next_url, depth - 1))

    return results

'''
Find and return all HTML forms on a page
'''
def find_forms(url: str, match_url: typing.Union[str, re.Pattern, None], exclude_url: typing.Union[str, re.Pattern, None]) -> typing.List[Form]:
    page, err, _ = soupify(url)

    if err is not None:
        print(f'Warning: Could not read page {url}: HTTP error {err}')

    base = url.split('/')[0] + '//' + url.split('/')[2] + '/'

    forms = []

    for form in page.find_all('form'):
        action = form.get('action')

        if action is None:
            action = url

        if re.search(r'^(https?:)?//', action):
            pass
        elif not action.startswith('/'):
            action = url + '/' + action
        else:
            action = base + action[1:]

        if match_url is not None and not re.search(match_url, action):
            continue

        if exclude_url is not None and re.search(exclude_url, action):
            continue

        form_obj = Form(action, form.get('method', 'GET'))

        for field in form.find_all('input'):
            if field.get('type') not in ['text', 'password', 'search'] or 'name' not in field.attrs:
                continue

            form_obj.add_field(field.get('name'))
        
        for field in form.find_all('textarea'):
            if 'name' not in field.attrs:
                continue

            form_obj.add_field(field.get('name'))
        
        forms.append(form_obj)
    
    return forms

'''
Find all form-like URLs by crawling
'''
def find_formlike(url: str, match_url: typing.Union[str, re.Pattern, None], exclude_url: typing.Union[str, re.Pattern, None]) -> typing.List[Form]:
    page, err, _ = soupify(url)

    if err is not None:
        print(f'Warning: Could not read page {url}: HTTP error {err}')
        
    base = url.split('/')[0] + '//' + url.split('/')[2] + '/'
    
    candidates = []

    for link in page.find_all('a'):
        candidate = link.get('href')

        if candidate is None:
            continue

        if re.search(r'^(https?:)?//', candidate):
            pass
        elif not candidate.startswith('/'):
            candidate = url + '/' + candidate
        else:
            candidate = base + candidate[1:]
        
        if match_url is not None and not re.search(match_url, candidate):
            continue

        if exclude_url is not None and re.search(exclude_url, candidate):
            continue

        candidates.append(candidate)
    
    form_unique = set()

    for candidate in candidates:
        if '?' in candidate:
            candidate = re.sub(r'=[^&]+&', '&', candidate)
            candidate = re.sub(r'=[^&]+', '', candidate)
            form_unique.add(candidate)

    results = []

    for candidate in form_unique:
        parts = candidate.split('?')
        form = Form(parts[0], 'GET', 'form-like URL')

        pairs = parts[1].split('&')
        for pair in pairs:
            form.add_field(pair)
        
        results.append(form)
    
    return results

'''
Uses various techniques to avoid a blacklist in a given string
'''
def bl_avoid(payload: str, blacklist: typing.List[str], capitalisation: bool = True) -> typing.List[str]:
    results = []

    # Substring search avoidance
    sa = payload
    for b in blacklist:
        sa = sa.replace(b, b[0] + b + b[1:])
    results.append(sa)

    # Random capitalisation
    if capitalisation:
        rc = payload
        for b in blacklist:
            r = ''.join([random.choice([c.upper(), c.lower()]) for c in list(b)])
            rc = rc.replace(b, r)
        results.append(rc)
    
    return results