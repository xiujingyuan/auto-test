from datetime import datetime

from app.common.easy_mock_util import EasyMock
from decimal import Decimal


class BusinessMock(EasyMock):

    def __init__(self, project, asset, asset_extend, asset_tran_list, period_start, period_end):
        super(BusinessMock, self).__init__(project)
        self.asset_extend = asset_extend
        self.asset_tran_list = asset_tran_list
        self.asset = asset
        self.period_start = period_start
        self.period_end = period_end if period_end is not None else asset.asset_period_count
        self.repay_type = 'early_settlement' if period_end == asset.asset_period_count else 'normal'

    @staticmethod
    def fen2yuan(amount):
        return float(Decimal(amount/100).quantize(Decimal("0.00")))

    def __get_trail_amount__(self):
        principal_amount = 0
        interest_amount = 0
        fee_amount = 0
        late_amount = 0
        repayPlanDict = {}
        for at in self.asset_tran_list:
            if at.asset_tran_period not in repayPlanDict:
                repayPlanDict[at.asset_tran_period] = {'principal': 0, 'interest': 0, 'fee': 0, 'late': 0}
            if at.asset_tran_category == 'principal':
                principal_amount += at.asset_tran_balance_amount
                overdue = self.cal_days(at.asset_tran_due_at, datetime.now())
                overdue = overdue if overdue >= 0 else 0
                repayPlanDict[at.asset_tran_period]['overdue'] = overdue
            if at.asset_tran_period == self.period_start:
                if at.asset_tran_category == 'interest':
                    interest_amount += at.asset_tran_balance_amount
                if at.asset_tran_category == 'fee':
                    fee_amount += at.asset_tran_balance_amount
                if at.asset_tran_category == 'late':
                    late_amount += at.asset_tran_balance_amount
            repayPlanDict[at.asset_tran_period][at.asset_tran_category] += at.asset_tran_balance_amount

        return principal_amount, interest_amount, fee_amount, late_amount, repayPlanDict

    def repay_plan_mock(self):
        pass

    def repay_trail_mock(self):
        pass

    def repay_trail_query_mock(self):
        pass

    def repay_apply_mock(self):
        pass
