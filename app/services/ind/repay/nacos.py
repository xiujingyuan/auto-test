from app.common.nacos_util import Nacos


class IndiaRepayNacos(Nacos):
    def __init__(self, env):
        self.program = 'repay'
        super(IndiaRepayNacos, self).__init__('ind', ''.join((self.program, env)))