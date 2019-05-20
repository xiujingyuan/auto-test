# -*- coding: utf-8 -*-
# @Time    : 2019/5/16 15:51
# @Author  : 张廷利
# @Site    : 
# @File    : ReportBiz.py
# @Software: IntelliJ IDEA
from app import db
from flask import current_app
from sqlalchemy import or_, and_, func
from app.models.ReportModel import ReportModel
from app.models.ReportTransModel import ReportTransModel
from app.models.ErrorCode import ErrorCode
from selenium import webdriver

from app.common.tools.UnSerializer import UnSerializer


class ReportBiz(UnSerializer):

    def write_report(self, request):
        report_id = -1
        try:
            request_json = request.json
            master = request_json['report']
            trans = request_json['trans']
            report = ReportModel()
            report.__dict__.update(UnSerializer.un_serialize(master))
            reportIsExists, existsReport = self.check_exists_bybranch_name(report.finlab_report_branch_name,
                                                                           report.finlab_report_build_number)
            if reportIsExists:
                report_id = existsReport.finlab_report_id
                result = self.update_report(master, report_id)
            else:
                result = self.add_report(report)
                report_id =result
                print("tianjia report report_id"+str(report_id))
            if result == ErrorCode.ERROR_CODE:
                return result

            for tran in trans:
                print("tran de report_id"+str(report_id))
                report_tran = ReportTransModel()
                report_tran.__dict__.update(UnSerializer.un_serialize(tran))
                reportTranIsExists, report_tran_exists = self.check_tran_exists_byreportid(report_id,
                                                                                           report_tran.finlab_report_transaction_type)
                if reportTranIsExists:
                    tran_reuslt = self.update_report_tran(tran, report_tran_exists.finlab_report_transaction_id)
                else:
                    report_tran.finlab_report_transaction_report_id = report_id
                    print("fuzhi houde  report_id"+str(report_tran.finlab_report_transaction_report_id))
                    tran_reuslt = self.add_report_tran(report_tran)
                if tran_reuslt == ErrorCode.ERROR_CODE:
                    return tran_reuslt
            return report_id
        except Exception as e:
            current_app.logger.exception(e)
            db.session.rollback()
            return ErrorCode.ERROR_CODE
        finally:
            db.session.commit()

    def update_report_tran(self, report_tran, report_tran_id):
        try:
            if 'finlab_report_transaction_id' in report_tran.keys():
                del report_tran['finlab_report_transaction_id']
            db.session.query(ReportTransModel).filter(
                ReportTransModel.finlab_report_transaction_id == report_tran_id).update(report_tran)
        except Exception as e:
            current_app.logger.exception(e)
            db.session.rollback()
            return ErrorCode.ERROR_CODE
        finally:
            db.session.commit()

    def add_report_tran(self, report_tran):
        try:

            db.session.add(report_tran)
        except Exception as e:
            current_app.logger.exception(e)
            db.session.rollback()
            return ErrorCode.ERROR_CODE
        finally:
            db.session.commit()

    def add_report(self, report):
        try:
            report.finlab_report_id=None
            db.session.add(report)
            db.session.flush()
            report_id = report.finlab_report_id
            return report_id
        except Exception as e:
            current_app.logger.exception(e)
            db.session.rollback()
            return ErrorCode.ERROR_CODE
        finally:
            db.session.commit()

    def update_report(self, report, report_id):
        try:
            if 'finlab_report_id' in report.keys():
                del report['finlab_report_id']
            db.session.query(ReportModel).filter(ReportModel.finlab_report_id == report_id).update(report)
        except Exception as e:
            current_app.logger.exception(e)
            db.session.rollback()
            return ErrorCode.ERROR_CODE
        finally:
            db.session.commit()

    def check_exists_bybranch_name(self, branch_name, build_number):
        try:
            result = False, -1
            query = db.session.query(ReportModel).filter(ReportModel.finlab_report_branch_name == branch_name) \
                .filter(ReportModel.finlab_report_build_number == build_number).first()
            if query is not None and query.finlab_report_id >= 0:
                result = True, query
            return result
        except Exception as e:
            current_app.logger.exception(e)
            db.session.rollback()
            return ErrorCode.ERROR_CODE
        finally:
            db.session.commit()

    def check_tran_exists_byreportid(self, report_id, report_type):
        try:
            result = False, -1
            query = db.session.query(ReportTransModel).filter(
                ReportTransModel.finlab_report_transaction_report_id == report_id).filter(
                ReportTransModel.finlab_report_transaction_type == report_type).first()
            if query is not None and query.finlab_report_transaction_id >= 0:
                result = True, query
            return result
        except Exception as e:
            current_app.logger.exception(e)
            db.session.rollback()
            return ErrorCode.ERROR_CODE
        finally:
            db.session.commit()

    def get_report_branch(self, branch_name):
        try:
            result = db.session.query(ReportModel).filter(
                ReportModel.finlab_report_branch_name == branch_name).fetchone()
            return result
        except Exception as e:
            current_app.logger.exception(e)
            db.session.rollback()
            return ErrorCode.ERROR_CODE
        finally:
            db.session.commit()


    def capture_screen_report(self,url,path):
        driver = webdriver.PhantomJS()
        driver.get(url)
        driver.save_screenshot(path)
