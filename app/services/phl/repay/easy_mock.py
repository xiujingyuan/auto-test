from app.common.easy_mock_util import EasyMock


class PhlRepayEasyMock(EasyMock):
    def __init__(self, check_req, return_req):
        super(PhlRepayEasyMock, self).__init__('rbiz_manual_test', check_req, return_req)
