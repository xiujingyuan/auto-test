import json
import time
from copy import deepcopy

from app.common.log_util import LogUtil
from app.services.china.repay.Model import WithholdOrder


def query_withhold(func):
    def wrapper(self, **kwargs):
        status = kwargs.pop('status', None)
        back_amount = kwargs.pop('back_amount', 0)
        item_no = kwargs.get('item_no', None)
        request, request_url, response = "", "", "error"
        try:
            request, request_url, response = func(self, **kwargs)
        except ValueError as e:
            # 'request run  error {0}, with url: {1}, req_data: {2}'
            e_list = str(e).split("#==#")
            request, request_url, response = json.loads(e_list[2].replace('req_data: ', '')), e_list[1].replace(
                "with url: ", ''), e_list[0].replace("request run  error: ", '')
            raise ValueError
        except Exception as e:
            response = str(e)
            raise Exception
        finally:
            withhold_info, lock_info, asset_info, task_msg_ret, biz_task_msg_ret, biz_asset_info_ret \
                = [], [], [], [], [], []
            if item_no:
                if isinstance(request, str):
                    req_key = ''
                else:
                    req_key = request[-1]['key'] if response and isinstance(response, list) else request['key']
            # withhold_key = self.get_withhold_info(item_no, req_key=req_key, repay_type=func.__name__)
            request_no_tuple, serial_no_tuple, id_num_tuple, _, _ = self.get_withhold_key_info(item_no, req_key=req_key)
            ret = dict(
                zip(('request', 'request_url', 'response', 'withhold_info', 'lock_info', 'asset_info'),
                    (request, request_url, response, withhold_info, lock_info, asset_info)))
            if status is not None and serial_no_tuple:
                ret['callback'] = []
                for serial in serial_no_tuple:
                    calls = dict(zip(('serial_no', 'status', 'back_amount'), (serial, status, back_amount)))
                    call_ret = getattr(self, 'repay_callback')(**calls)
                    ret['callback'].append(call_ret)
            return ret

    return wrapper


def modify_return(func):
    def wrapper(self, *args, **kwargs):
        record_type = kwargs.pop('record_type', 'to_spec_dict')
        func_name = func.__name__
        # if 'max_create_at' not in kwargs and func_name != 'get_asset_tran':
        #     kwargs['max_create_at'] = self.get_date(fmt='%Y-%m-%d', is_str=True)
        ret = func(self, *args, **kwargs)
        if record_type == 'obj':
            return ret
        elif record_type in ('to_spec_dict', 'to_dict'):
            ret = list(map(lambda x: getattr(x, record_type), ret))
            return {func_name[4:]: ret}
    return wrapper


def time_print(func):
    def wrapper(self, *args, **kwargs):
        LogUtil.log_info(func.__name__ + ' begin: ')
        ret = func(self, *args, **kwargs)
        LogUtil.log_info(func.__name__ + ' end: ')
        return ret
    return wrapper


def wait_time(timeout=10):
    def outer_wrapper(func):
        def wrapper(self, *args, **kwargs):
            LogUtil.log_info(func.__name__ + ' begin: ')
            count = 0
            while True:
                ret = func(self, *args, **kwargs)
                if ret:
                    return ret
                time.sleep(0.1)
                count += 1
                if count >= 10 * timeout:
                    print('time is out but obj not found!')
                    return ret
        return wrapper
    return outer_wrapper


def run_callback(func):
    def wrapper(self, **kwargs):
        ret, status = func(self, **kwargs)
        for serial in ret['withhold_info']['serial_no']:
            calls = dict(zip(('serial_no', 'status'), (serial, status)))
            getattr(self, 'repay_callback')(**calls)
        return ret

    return wrapper
