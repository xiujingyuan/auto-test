from app.common.nacos_util import Nacos


class PakGrantNacos(Nacos):
    def __init__(self, env):
        self.program = 'grant'
        super(PakGrantNacos, self).__init__('pak', ''.join((self.program, env)))
