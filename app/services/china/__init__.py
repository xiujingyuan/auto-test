

def get_trace(func):
    def wrapper(self, *kw, **kwargs):
        extend = kwargs.get('extend')
        op_type = kwargs.get('op_type')
        table_name = kwargs.get('table_name')
        loading_key = kwargs.get('loading_key')
        creator = kwargs.get('creator')
        if op_type == 'get_trace_info':
            order_no = f'{table_name.replace("central_", "")}_order_no' if \
                table_name.startswith('central_') else 'order_no'
            task_type = f'{table_name.replace("central_", "")}_type' if \
                table_name.startswith('central_') else 'type'
            service_name = f'biz-central' if \
                table_name.startswith('central_') else f'{self.program}{self.env}'
            service_name = f'gbiz{self.env}' if \
                table_name.startswith('grant_') else service_name
            create_at = extend[f'{table_name.replace("central_", "")}_create_at'] if table_name.startswith('central_') \
                else extend['create_at']
            update_at = extend[f'{table_name.replace("central_", "")}_update_at'] if table_name.startswith('central_') \
                else extend['update_at']
            ret = self.get_trace_info(extend['channel'], extend[loading_key], creator, service_name,
                                      extend[order_no], extend[task_type], create_at, update_at)
        else:
            ret = func(self, *kw, **kwargs)
        return ret
    return wrapper
