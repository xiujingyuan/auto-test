# -*- coding: utf-8 -*-
# @Time    : 2019/5/16 15:51
# @Author  : 张廷利
# @Site    : 
# @File    : ReportBiz.py
# @Software: IntelliJ IDEA
import platform

from app import db
from flask import current_app
from sqlalchemy import or_, and_, func
from app.models.ReportModel import ReportModel
from app.models.ReportTransModel import ReportTransModel
from app.models.ErrorCode import ErrorCode
from selenium import webdriver

from app.common.tools.Serializer import Serializer
from app.common.tools.UnSerializer import UnSerializer


class ReportBiz(Serializer,UnSerializer):



    def transfer_params(self,request):
        request_json = request.json
        master = request_json['report']
        trans = request_json['trans']
        return self.write_report(master,trans)


    def write_report(self, master,trans):
        report_id = -1
        try:

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


            if result == ErrorCode.ERROR_CODE:
                current_app.logger.info(result)
                return result
            current_app.logger.info(trans)
            for tran in trans:
                current_app.logger.info(tran)
                report_tran = ReportTransModel()
                report_tran.__dict__.update(UnSerializer.un_serialize(tran))
                reportTranIsExists, report_tran_exists = self.check_tran_exists_byreportid(report_id,
                                                                                           report_tran.finlab_report_transaction_type)
                if reportTranIsExists:
                    tran_reuslt = self.update_report_tran(tran, report_tran_exists.finlab_report_transaction_id)
                else:
                    report_tran.finlab_report_transaction_report_id = report_id
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
            if 'trans' in report.keys():
                del report['trans']
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
                ReportModel.finlab_report_branch_name == branch_name).first()
            return result
        except Exception as e:
            current_app.logger.exception(e)
            db.session.rollback()
            return ErrorCode.ERROR_CODE
        finally:
            db.session.commit()


    def capture_screen_report(self,url,path):
        try:
            system_name = platform.system()
            if system_name.lower() =='linux':
                driver = webdriver.PhantomJS(executable_path="/usr/local/python3/bin/phantomjs")
            else:
                driver = webdriver.PhantomJS()
            driver.get(url)
            current_app.logger.info(url)
            current_app.logger.info(path)
            driver.save_screenshot(path)
            return 0
        except Exception as e:
            current_app.logger.exception(e)
            return 9999

    def get_report_detail(self,request):
        request_json = request.json
        params =[]
        result ={}
        try:
            if request_json is not None:
                if 'report_id' in request_json.keys():
                    value = request_json['report_id']
                    if value is not None or value!="":
                        params.append(ReportModel.finlab_report_id == value)
                    else:
                        if 'branch_name' in request_json.keys():
                            value = request_json['branch_name']
                            if value is not None or value!="":
                                params.append(ReportModel.finlab_report_branch_name == value)

                master = db.session.query(ReportModel).filter(*params).first()
                report = Serializer.serialize(master)
                if master is not None:
                    result=db.session.query(ReportTransModel).filter(ReportTransModel.finlab_report_transaction_report_id == master.finlab_report_id).all()
                    trans = Serializer.serialize_list(result)
                report['trans'] = trans
            return report
        except Exception as e:
            current_app.logger.exception(e)
            db.session.rollback()
            return ErrorCode.ERROR_CODE
        finally:
            db.session.commit()


    def search_report(self,request):
        request_json = request.json
        params =[]
        page_index =1
        page_size=10
        sort_field=""
        try:
            if request_json is not None:
                if 'report_id' in request_json.keys():
                    value = request_json['report_id']
                    if value is not None and value!="":
                        params.append(ReportModel.finlab_report_id.like('%'+value+'%'))
                    else:
                        if 'branch_name' in request_json.keys():
                            value = request_json['branch_name']
                            if value is not None and value!="":
                                params.append(ReportModel.finlab_report_branch_name.like('%'+value+'%'))
                        if 'tester' in request_json.keys():
                            value = request_json['tester']
                            if value is not None and value!="":
                                params.append(ReportModel.finlab_report_tester == value)
                        if 'productor' in request_json.keys():
                            value = request_json['productor']
                            if value is not None and value!="":
                                params.append(ReportModel.finlab_report_productor == value)
                        if 'devloper' in request_json.keys():
                            value = request_json['devloper']
                            if value is not None and value!="":
                                params.append(ReportModel.finlab_report_devloper == value)
                        if 'begin_date' in request_json.keys():
                            value = request_json['begin_date']
                            if value is not None and value!="":
                                params.append(ReportModel.finlab_report_begin >= value)
                        if 'end_date' in request_json.keys():
                            value = request_json['end_date']
                            if value is not None and value!="":
                                params.append(ReportModel.finlab_report_begin <= value)
                        if 'system_name' in request_json.keys():
                            value = request_json['system_name']
                            if value is not None and value!="":
                                params.append(ReportModel.finlab_report_system_name.like('%'+value+'%'))

                    if 'page_index' in request_json.keys():
                        page_index = request_json['page_index']
                    if 'page_size' in request_json.keys():
                        page_size = request_json['page_size']

                query = db.session.query(ReportModel)
                query = query.filter(*params)
                result_page = query.order_by(ReportModel.finlab_report_begin.desc()).paginate(page=page_index, per_page=page_size, error_out=False)
                result = result_page.items
                count = result_page.total
                cases = ReportModel.serialize_list(result)
                data = {}
                data['page_index'] = page_index
                data['cases'] = cases
                data['page_size'] = len(cases)
                data['total'] = count
                return data


        except Exception as e:
            current_app.logger.exception(e)
            db.session.rollback()
            return ErrorCode.ERROR_CODE
        finally:
            db.session.commit()