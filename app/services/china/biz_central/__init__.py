

def biz_modify_return(func):
    def wrapper(self, **kwargs):
        record_type = kwargs.pop('record_type', 'to_spec_dict')
        func_name = func.__name__
        if 'max_create_at' not in kwargs and func_name not in ('get_capital', 'get_capital_tran'):
            kwargs['max_create_at'] = self.get_date(fmt='%Y-%m-%d', is_str=True)
        ret = func(self, **kwargs)
        if record_type == 'obj':
            return ret
        elif record_type in ('to_spec_dict', 'to_dict'):
            ret = list(map(lambda x: getattr(x, record_type), ret))
            return {'biz_{0}'.format(func_name[4:]): ret}
    return wrapper
