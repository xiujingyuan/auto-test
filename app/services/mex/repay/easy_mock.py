from app.common.easy_mock_util import EasyMock


class MexRepayEasyMock(EasyMock):
    def __init__(self, mock_name, check_req, return_req):
        super(MexRepayEasyMock, self).__init__(mock_name, check_req, return_req)
