from app.common.nacos_util import Nacos


class ChinaGrantNacos(Nacos):
    def __init__(self, env):
        self.program = 'grant'
        super(ChinaGrantNacos, self).__init__('china', ''.join((self.program, env)))
        self.gateway_nacos = Nacos('china', 'gateway')
