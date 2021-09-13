from app.common.easy_mock_util import EasyMock

WEISHEMMA_TRAIL = '''{
  "state": "success",
  "code": "1002",
  "msg": "查询成功！",
  "shddh": function({
    _req
  }) {
    return _req.body.shddh
  },
  "rest_principal": 800000,
  "total_amount": 800100
}'''


class RepayEasyMock(EasyMock):
    def __init__(self, check_req, return_req):
        super(RepayEasyMock, self).__init__('rbiz_auto_test', check_req, return_req)

    def update_trail_amount(self, channel, principal, interest):
        getattr(self, 'update_{0}_trail_amount'.format(channel))(principal, interest)

    def update_trail_status(self, channel, value):
        super(RepayEasyMock, self).update('/weishenma_daxinganling/pre-loan/repayTrial', '', value)

    def update_weishenma_daxinganling_trail_amount(self, principal, interest):
        value = dict(zip(('$.rest_principal', '$.total_amount'), (principal, principal + interest)))
        super(RepayEasyMock, self).update_by_json_path('/weishenma_daxinganling/pre-loan/repayTrial', value,
                                                       method='post')
