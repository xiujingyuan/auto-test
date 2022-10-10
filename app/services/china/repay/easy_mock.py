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


class ChinaRepayEasyMock(EasyMock):
    def __init__(self, mock_name, check_req, return_req):
        super(ChinaRepayEasyMock, self).__init__(mock_name, check_req, return_req)

    def update_trail_status(self, channel, value):
        super(ChinaRepayEasyMock, self).update('/weishenma_daxinganling/pre-loan/repayTrial', '', value)

    def update_trail_amount(self, channel, principal, interest, fee, status):
        if channel == 'weishenma_daxinganling':
            value = dict(zip(('$.rest_principal', '$.total_amount'), (principal, principal + interest)))
            trail_url = '/weishenma_daxinganling/pre-loan/repayTrial'
        elif channel == 'longjiang_daqin':
            principal = round(float(principal / 100), 2)
            interest = round(float(interest / 100))
            value = dict(
                zip(('$.data.assets[0].principal', '$.data.assets[0].interest', '$.data.assets[0].total_amount'),
                    (principal, interest, principal + interest)))
            trail_url = '/longjiang/std/repayment/calculate'
        elif channel == 'qinnong':
            value = dict(zip(('$.data.assets[0].principal', '$.data.assets[0].interest', '$.data.assets[0].total_amount'),
                             (principal, interest, principal + interest)))
            trail_url = '/qinnong/std/repayment/calculate'
        elif channel == 'yilian_dingfeng':
            principal = round(float(principal / 100), 2)
            interest = round(float(interest / 100), 2)
            value = dict(zip(('$.data.repaytotal', '$.data.repaycapital', '$.data.repayinterest'),
                             (principal + interest, principal, interest)))
            trail_url = '/qingjia/yilian_dingfeng/repayTrial'
        elif channel == 'lanzhou_haoyue_qinjia':
            principal = round(float(principal / 100), 2)
            interest = round(float(interest / 100), 2)
            value = dict(zip(('$.data.repaytotal', '$.data.repaycapital', '$.data.repayinterest'),
                             (principal + interest, principal, interest)))
            trail_url = '/qingjia/lanzhou_haoyue_qinjia/repayTrial'
        elif channel == 'zhongyuan_zunhao':
            value = dict(zip(('$.data.totalRepayAmt', '$.data.totalPlanamt',
                              '$.data.totalPsPrcpAmt', '$.data.totalPsNormInt'), (
                             principal + interest, principal + interest,
                              principal,
                             interest)))
            trail_url = '/zhongzhirong/zhongyuan_zunhao/repayTrial'
        elif channel == 'yumin_zhongbao':
            value = dict(zip(('$.data.repymtPnpAmt', '$.data.repymtIntAmt'),
                             (principal, interest)))
            trail_url = '/zhongzhirong/yumin_zhongbao/ym.repay.trial'
        elif channel == 'yixin_rongsheng':
            value = dict(zip(('$.data.lnsCurAmt', '$.data.lnsCurInt'),
                             (principal, interest)))
            trail_url = '/yixin/yixin_rongsheng/calAllAmountInAdvanceSingle'
        return super(ChinaRepayEasyMock, self).update_by_json_path(trail_url, value, method='post')
