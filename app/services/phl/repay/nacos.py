from app.common.nacos_util import Nacos


class PhlRepayNacos(Nacos):
    def __init__(self, env):
        self.program = 'repay'
        super(PhlRepayNacos, self).__init__('phl', ''.join((self.program, env)))