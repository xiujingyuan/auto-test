from app.common.easy_mock_util import EasyMock


class PakGrantEasyMock(EasyMock):
    def __init__(self, mock_name, check_req, return_req):

        super(PakGrantEasyMock, self).__init__(mock_name, check_req, return_req)
