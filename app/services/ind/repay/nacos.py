from app.common.nacos_util import Nacos


class IndRepayNacos(Nacos):
    def __init__(self, env):
        self.program = 'repay'
        super(IndRepayNacos, self).__init__('ind', ''.join((self.program, env)))