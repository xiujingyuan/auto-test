from app.common.nacos_util import Nacos


class ThailandRepayNacos(Nacos):
    def __init__(self, env):
        self.program = 'repay'
        super(ThailandRepayNacos, self).__init__('thailand', ''.join((self.program, env)))