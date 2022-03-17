from app.common.nacos_util import Nacos


class IndGrantNacos(Nacos):
    def __init__(self, env):
        self.program = 'grant'
        super(IndGrantNacos, self).__init__('ind', ''.join((self.program, env)))
