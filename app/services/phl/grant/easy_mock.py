from app.common.easy_mock_util import EasyMock


class PhlGrantEasyMock(EasyMock):
    def __init__(self, mock_name, check_req, return_req):
        super(PhlGrantEasyMock, self).__init__(mock_name, check_req, return_req)
