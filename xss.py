import selenium, selenium.webdriver, time, typing

import utils

'''
Gives information about a vulnerable form field
'''
class XSSVuln():
    def __init__(self, form: utils.Form, field: str) -> None:
        self._form = form
        self._field = field
    
    @property
    def form(self) -> utils.Form:
        return self._form
    
    def json(self) -> typing.Dict[str, str]:
        return {
            'field' : self._field,
            'type' : 'XSS'
        }

    def __repr__(self) -> str:
        return f'\x1B[91mVulnerability detected!\x1B[0m\nOn field {self._field} in {self._form}\nXSS'

'''
Tests a list of forms for XSS vulnerabilities
'''
def test_scripts(targets: typing.List[utils.Form], limits: int, delay: typing.Optional[int]) -> typing.List[XSSVuln]:
    results = []

    driver_opts = selenium.webdriver.ChromeOptions()
    driver_opts.add_argument('headless')

    driver = selenium.webdriver.Chrome(chrome_options=driver_opts)

    timestamp = str(time.time())

    for form in targets:
        for field in form.get_fields():
            url, err = form.soupless_request({x : (f'<script>document.body.innerHTML+="<br id=\'vmap.{timestamp}.{form}.{field}\' />";</script>' if x == field else '') for x in form.get_fields()})

            if err is not None:
                continue

            driver.get(url)
            if driver.find_element_by_id(f'vmap.{timestamp}.{form}.{field}'):
                results.append(XSSVuln(form, field))
            driver.close()
            
            if delay is not None:
                time.sleep(delay)
    
    driver.quit()
    return results