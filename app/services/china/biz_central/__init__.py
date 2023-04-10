

def biz_modify_return(func):
    def wrapper(self, *args, **kwargs):
        record_type = kwargs.pop('record_type', 'to_spec_dict')
        exclude_col = kwargs.pop('exclude_col', [])
        func_name = func.__name__
        ret = func(self, *args, **kwargs)
        if record_type == 'obj':
            return ret
        elif record_type in ('to_spec_dict', 'to_dict'):
            ret = list(map(lambda x: getattr(x, record_type), ret))
            return {func_name[4:]: ret}
        elif record_type == 'to_spec_dict_obj':
            ret = list(map(lambda x: getattr(x, 'to_spec_dict_obj')(exclude_col), ret))
            return {func_name[4:]: ret}
    return wrapper


