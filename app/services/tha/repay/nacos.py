from app.common.nacos_util import Nacos


class ThaRepayNacos(Nacos):
    def __init__(self, env):
        self.program = 'repay'
        super(ThaRepayNacos, self).__init__('tha', ''.join((self.program, env)))