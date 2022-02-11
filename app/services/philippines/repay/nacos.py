from app.common.nacos_util import Nacos


class PhilippinesRepayNacos(Nacos):
    def __init__(self, env):
        self.program = 'repay'
        super(PhilippinesRepayNacos, self).__init__('philippines', ''.join((self.program, env)))