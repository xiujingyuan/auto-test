from app.common.easy_mock_util import EasyMock


class ChinaGrantEasyMock(EasyMock):
    def __init__(self, check_req, return_req):
        super(ChinaGrantEasyMock, self).__init__('gbiz_auto_test', check_req, return_req)
