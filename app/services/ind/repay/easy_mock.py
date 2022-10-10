from app.common.easy_mock_util import EasyMock


class IndRepayEasyMock(EasyMock):
    def __init__(self, mock_name, check_req, return_req):
        super(IndRepayEasyMock, self).__init__(mock_name, check_req, return_req)
