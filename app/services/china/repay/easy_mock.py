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
        super(RepayEasyMock, self).__init__('rbiz_manual_test', check_req, return_req)

    def update_trail_status(self, channel, value):
        super(RepayEasyMock, self).update('/weishenma_daxinganling/pre-loan/repayTrial', '', value)

    def update_trail_amount(self, channel, principal, interest, status):
        if channel == 'weishenma_daxinganling':
            value = dict(zip(('$.rest_principal', '$.total_amount'), (principal, principal + interest)))
            trail_url = '/weishenma_daxinganling/pre-loan/repayTrial'
        elif channel == 'longjiang_daqin':
            value = dict(
                zip(('$.data.assets[0].principal', '$.data.assets[0].interest', '$.data.assets[0].total_amount'),
                    (round(float(principal / 100), 2), round(float(interest / 100), 2),
                     round(float((principal + interest) / 100), 2))))
            trail_url = '/longjiang/std/repayment/calculate'
        elif channel == 'qinnong':
            value = dict(zip(('$.data.assets[0].principal', '$.data.assets[0].interest', '$.data.assets[0].total_amount'),
                             (principal, interest, principal + interest)))
            trail_url = '/qinnong/std/repayment/calculate'
        return super(RepayEasyMock, self).update_by_json_path(trail_url, value, method='post')
