from app.common.nacos_util import Nacos


class MexGrantNacos(Nacos):
    def __init__(self, env):
        self.program = 'grant'
        super(MexGrantNacos, self).__init__('mex', ''.join((self.program, env)))
