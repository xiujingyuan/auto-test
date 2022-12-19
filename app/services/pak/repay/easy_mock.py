from app.common.easy_mock_util import EasyMock


class PakRepayEasyMock(EasyMock):
    def __init__(self, mock_name, check_req, return_req):
        super(PakRepayEasyMock, self).__init__(mock_name, check_req, return_req)
