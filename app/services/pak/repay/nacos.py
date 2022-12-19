from app.common.nacos_util import Nacos


class PakRepayNacos(Nacos):
    def __init__(self, env):
        self.program = 'repay'
        super(PakRepayNacos, self).__init__('pak', ''.join((self.program, env)))