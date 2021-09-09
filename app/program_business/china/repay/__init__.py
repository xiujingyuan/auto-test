import json

from app.program_business.china.repay.Model import WithholdOrder


def query_withhold(func):
    def wrapper(self, **kwargs):
        status = kwargs.pop('status', None)
        item_no = kwargs.get('item_no', None)
        request, request_url, response = func(self, **kwargs)
        withhold_info, lock_info, withhold, asset_info = [], [], [], []
        if item_no:
            if isinstance(request, str):
                req_key = ''
            else:
                req_key = request[-1]['key'] if response and isinstance(response, list) else request['key']
        withhold = self.get_withhold_info(item_no, req_key=req_key, repay_type=func.__name__)
        ret = dict(zip(('request', 'request_url', 'response', 'withhold', 'withhold_info', 'lock_info', 'asset_info'),
                       (request, request_url, response, withhold, withhold_info, lock_info, asset_info)))
        if status is not None and ret['withhold'] and ret['withhold']['serial_no']:
            ret['callback'] = []
            for serial in ret['withhold']['serial_no']:
                calls = dict(zip(('serial_no', 'status'), (serial, status)))
                call_ret = getattr(self, 'repay_callback')(**calls)
                ret['callback'].append(call_ret)
        if item_no:
            ret['withhold_info'] = self.get_current_withhold_info(item_no, tuple(ret['withhold']['request_no']))
            ret['asset_info'] = self.get_asset_info(item_no)
            ret['lock_info'] = self.get_lock_info(item_no)
        return ret
    return wrapper

# def query_withhold(is_callback=True):
#     def wrapper(func):
#         def _wrapper(self, **kwargs):
#             ret = WITHHOLD_RET
#             status = None if func.__name__ == 'repay_callback' else kwargs.pop('status', None)
#             ret['request'], ret['request_url'], ret['response'], ret['withhold_info'] = func(self, **kwargs)
#             if is_callback and status is not None:
#                 for serial in ret['withhold_info']['serial_no']:
#                     calls = dict(zip(('serial_no', 'status'), (serial, status)))
#                     getattr(self, 'repay_callback')(**calls)
#             return ret
#         return _wrapper
#     return wrapper


def run_callback(func):
    def wrapper(self, **kwargs):
        ret, status = func(self, **kwargs)
        for serial in ret['withhold_info']['serial_no']:
            calls = dict(zip(('serial_no', 'status'), (serial, status)))
            getattr(self, 'repay_callback')(**calls)
        return ret
    return wrapper















