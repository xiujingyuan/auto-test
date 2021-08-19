
def query_withhold(func):
    def wrapper(self, **kwargs):
        ret = WITHHOLD_RET
        ret['request'], ret['request_url'], ret['response'], ret['withhold_info'] = func(self, **kwargs)
        return ret
    return wrapper


WITHHOLD_RET = {"request": {}, "response": {}, "request_url": ""}















