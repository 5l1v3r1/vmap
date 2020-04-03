import time, typing

import utils

'''
Gives information about a vulnerable form field
'''
class LFIVuln():
    def __init__(self, value: str, form: utils.Form, field: str) -> None:
        self._value = value
        self._form = form
        self._field = field
    
    @property
    def form(self) -> utils.Form:
        return self._form
    
    def json(self) -> typing.Dict[str, str]:
        return {
            'field' : self._field,
            'value' : self._value,
            'type' : 'LFI'
        }

    def __repr__(self) -> str:
        return f'\x1B[91mVulnerability detected!\x1B[0m\nOn field {self._field} in {self._form}\nLFI using {self._value}'

'''
Generates paths to try
'''
def walk_paths(limits: int, fname: str) -> typing.List[str]:
    candidates = [fname]

    for i in range(limits * 3):
        candidates.append(('../' * i) + fname[1:])
    
    return candidates

'''
Tests a list of forms for LFI vulnerabilities
'''
def test_lfi(targets: typing.List[utils.Form], limits: int, delay: typing.Optional[int], fname: str, flag:str) -> typing.List[LFIVuln]:
    results = []
    paths = walk_paths(limits, fname)

    for form in targets:
        for field in form.get_fields():
            for path in paths:
                response, err, _ = form.request({x : (path if x == field else '') for x in form.get_fields()}, None)

                if err is None and flag in response.text:
                    results.append(LFIVuln(path, form, field))
                
                if delay is not None:
                    time.sleep(delay)
    
    return results