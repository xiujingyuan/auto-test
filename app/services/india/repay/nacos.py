from app.common.nacos_util import Nacos


class IndiaRepayNacos(Nacos):
    def __init__(self, env):
        self.program = 'repay'
        super(IndiaRepayNacos, self).__init__('india', ''.join((self.program, env)))