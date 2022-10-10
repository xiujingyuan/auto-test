from app.common.easy_mock_util import EasyMock


class ChinaGrantEasyMock(EasyMock):
    def __init__(self, mock_name, check_req, return_req):
        super(ChinaGrantEasyMock, self).__init__(mock_name, check_req, return_req)
