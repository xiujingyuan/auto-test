from app.common.nacos_util import Nacos


class PhlGrantNacos(Nacos):
    def __init__(self, env):
        self.program = 'grant'
        super(PhlGrantNacos, self).__init__('phl', ''.join((self.program, env)))
