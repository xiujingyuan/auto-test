from app.common.nacos_util import Nacos


class ChinaCleanNacos(Nacos):
    def __init__(self, env):
        self.program = 'clean'
        super(ChinaCleanNacos, self).__init__('china', ''.join((self.program, env)).replace('_', '-'))
