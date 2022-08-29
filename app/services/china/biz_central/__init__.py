

def biz_modify_return(func):
    def wrapper(self, *args, **kwargs):
        record_type = kwargs.pop('record_type', 'to_spec_dict')
        func_name = func.__name__
        ret = func(self, *args, **kwargs)
        if record_type == 'obj':
            return ret
        elif record_type in ('to_spec_dict', 'to_dict'):
            ret = list(map(lambda x: getattr(x, record_type), ret))
            return {func_name[4:]: ret}
    return wrapper


