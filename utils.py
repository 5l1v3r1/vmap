import bs4, requests, typing

'''
Represents a HTML form
'''
class Form():
    def __init__(self, url: str, method: str) -> None:
        self._url = url
        self._method = method
        self._fields = []

    def add_field(self, name: str) -> None:
        self._fields.append(name)

    def get_fields(self) -> typing.List[str]:
        return self._fields

    def request(self, values: typing.Dict[str, str], cookie: typing.Optional[str]) -> bs4.BeautifulSoup:
        return soupify(self._url, self._method, values, cookie)

    def __repr__(self) -> str:
        return f'{self._method} {self._url} (' + ', '.join(self._fields) + ')'

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