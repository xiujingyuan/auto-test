from app.common.nacos_util import Nacos


class ThaGrantNacos(Nacos):
    def __init__(self, env):
        self.program = 'grant'
        super(ThaGrantNacos, self).__init__('tha', ''.join((self.program, env)))
