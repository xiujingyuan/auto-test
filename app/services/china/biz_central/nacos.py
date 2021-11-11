from app.common.nacos_util import Nacos


class ChinaBizCentralNacos(Nacos):
    def __init__(self, env):
        self.program = 'biz_central'
        super(ChinaBizCentralNacos, self).__init__('china', ''.join((self.program, env)).replace('_', '-'))
