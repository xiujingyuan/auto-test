from app.common.easy_mock_util import EasyMock


class RepayEasyMock(EasyMock):
    def __init__(self, check_req, return_req):
        super(RepayEasyMock, self).__init__('rbiz_auto_test', check_req, return_req)