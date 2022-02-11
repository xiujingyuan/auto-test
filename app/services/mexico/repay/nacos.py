from app.common.nacos_util import Nacos


class MexicoRepayNacos(Nacos):
    def __init__(self, env):
        self.program = 'repay'
        super(MexicoRepayNacos, self).__init__('mexico', ''.join((self.program, env)))