import bs4, requests, re, time, typing

'''
Represents a HTML form
'''
class Form():
    def __init__(self, url: str, method: str, ftype: str = 'form') -> None:
        self._url = url
        self._method = method
        self._type = ftype
        self._fields = []

    def add_field(self, name: str) -> None:
        self._fields.append(name)

    def get_fields(self) -> typing.List[str]:
        return self._fields

    def request(self, values: typing.Dict[str, str], cookie: typing.Optional[str]) -> bs4.BeautifulSoup:
        return soupify(self._url, self._method, values, cookie)

    def __repr__(self) -> str:
        return f'{self._type} {self._method} {self._url} (' + ', '.join(self._fields) + ')'

SoupifyResult = typing.Union[typing.Tuple[None, int, None], typing.Tuple[bs4.BeautifulSoup, None, typing.Optional[str]]]

'''
Make a request to a URL and turn it into beautiful soup
'''
def soupify(url: str, method: str = 'GET', payload: typing.Dict[str, str] = {}, cookie: typing.Optional[str] = None) -> SoupifyResult:
    s = requests.Session()

    if method == 'GET':
        res = s.get(url, params=payload)
        if res.status_code // 100 == 4 or res.status_code // 100 == 5:
            return None, res.status_code, None
        return bs4.BeautifulSoup(res.text, 'lxml'), None, s.cookies[cookie] if (cookie is not None and cookie in s.cookies) else None
    elif method == 'POST':
        res = s.post(url, data=payload)
        if res.status_code // 100 == 4 or res.status_code // 100 == 5:
            return None, res.status_code, None
        return bs4.BeautifulSoup(res.text, 'lxml'), None, s.cookies[cookie] if (cookie is not None and cookie in s.cookies) else None

'''
Find and return all HTML forms on a page
'''
def find_forms(url: str) -> typing.List[Form]:
    page, err, _ = soupify(url)

    if err is not None:
        raise Exception(f'Could not read page {url}: HTTP error {err}')

    forms = []
    base = url.split('/')[0] + '//' + url.split('/')[2]

    for form in page.find_all('form'):
        form_obj = Form(base + form.get('action') if form.get('action')[0] == '/' else form.get('action'), form.get('method', 'GET'))

        for field in form.find_all('input'):
            if field.get('type') not in ['text', 'password', 'search'] or 'name' not in field.attrs:
                continue

            form_obj.add_field(field.get('name'))
        
        forms.append(form_obj)
    
    return forms

'''
Find all form-like URLs by crawling
'''
def find_formlike(url: str, delay: typing.Optional[int]) -> typing.List[Form]:
    visited = set()
    queue = []

    queue.append(url)

    while len(queue) > 0:
        this_url = queue.pop()

        visited.add(this_url)
        page, err, _ = soupify(this_url)

        if err:
            continue
        
        for link in page.find_all('a'):
            next_url = link.get('href')

            if next_url.startswith('/'):
                next_url = url + next_url[1:]

            if next_url is not None and next_url not in visited:
                queue.append(next_url)
        
        if delay is not None:
            time.sleep(delay)
    
    form_unique = set()

    for candidate in visited:
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