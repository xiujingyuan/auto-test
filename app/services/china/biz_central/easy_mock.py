from app.common.easy_mock_util import EasyMock


class ChinaBizCentralEasyMock(EasyMock):
    def __init__(self, check_req, return_req):
        super(ChinaBizCentralEasyMock, self).__init__('gbiz_auto_test', check_req, return_req)
