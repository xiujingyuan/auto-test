from app.common.nacos_util import Nacos


class MexRepayNacos(Nacos):
    def __init__(self, env):
        self.program = 'repay'
        super(MexRepayNacos, self).__init__('mex', ''.join((self.program, env)))