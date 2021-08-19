from app.common.easy_mock_util import EasyMock


class GrantEasyMock(EasyMock):
    def __init__(self, check_req, return_req):
        super(GrantEasyMock, self).__init__('gbiz_auto_test', check_req, return_req)
