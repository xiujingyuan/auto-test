from app.services.capital_service.jinmeixin_daqin import JinmeixindaqinMock


class JinmeixinhanchenMock(JinmeixindaqinMock):

    def __init__(self, project, asset, asset_extend, asset_tran_list, period_start, period_end):
        super(JinmeixinhanchenMock, self).__init__(project, asset, asset_extend, asset_tran_list,
                                                   period_start, period_end)
        self.channel = 'jinmeixin_hanchen'
