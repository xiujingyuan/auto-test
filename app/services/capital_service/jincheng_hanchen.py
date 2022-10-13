from app.services.capital_service.jinmeixin_daqin import JinmeixindaqinMock


class JinchenghanchenMock(JinmeixindaqinMock):

    def __init__(self, project, asset, asset_extend, asset_tran_list, period_start, period_end):
        self.channel = 'jincheng_hanchen'
        super(JinchenghanchenMock, self).__init__(project, asset, asset_extend, asset_tran_list, period_start, period_end)

