# -*- coding: utf-8 -*-
# @Time    : 公元19-04-11 下午5:34
# @Author  : 张廷利
# @Site    :
# @File    : FourElement.py
# @Software: IntelliJ IDEA



# -*- coding: utf-8 -*-
# @Title: FourElement
# @ProjectName framework-test
# @Description: TODO
# @author fyi zhang
# @date 2018/12/30 22:00

import random
from faker import Faker
from datetime import datetime
from dateutil.relativedelta import relativedelta


class FourElement(object):
    def __init__(self):
        self.faker = Faker('zh_CN')

    def get(self):
        data = {}
        data['bank_code'] = self.generate_bank_code()
        data['phone_number'] = self.get_phone_number()
        data['user_name'] = self.get_name()
        data['id_number'] = self.generate_idnumber()
        response ={}
        response['code']=0
        response['message']="success"
        response['data'] = data
        return response



    def generate_idnumber(self,card_zone=None,birth_day=None):

        id = random.randint(0,13)
        card_zone = ['110101',
                     '110102',
                     '110105',
                     '110106',
                     '110107',
                     '110108',
                     '110109',
                     '110111',
                     '110112',
                     '110103',
                     '110200',
                     '110221',
                     '110224',
                     '110226']


        year_max = datetime.now().year -25
        year_min =datetime.now().year-45
        birth_day_year = str(random.randint(year_min,year_max))+'-01-01 0:00:00'
        birth_day_month = random.randint(0,365)
        value = datetime.strptime(birth_day_year,"%Y-%m-%d %H:%M:%S") + relativedelta(days=+birth_day_month)
        birth_day= str(value.year) +str(value.month).zfill(2)+str(value.day).zfill(2)
        random_code = str(random.randint(100,999)).zfill(3)
        idnumber = card_zone[id] + birth_day + random_code
        return self.get_verify_code(idnumber)


    #添加效验码
    def get_verify_code(self,id_number):
        i = 0
        count = 0
        weight = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2] #权重项
        mapping_code ={'0':'1','1':'0','2':'X','3':'9','4':'8','5':'7','6':'6','7':'5','8':'4','9':'3','10':'2'} #校验码映射

        for i in range(0,len(id_number)):
            #前十七位乘以权重之和
            count = count +int(id_number[i])*weight[i]
        #权重之和使用11 取模，然后在mappingcode中获取最后一位校验位
        return id_number + mapping_code[str(count%11)]

    def get_phone_number(self):
        # prelist=["130","131","132","133","134","135","136","137","138","139","147","150","151","152","153","155","156","157","158","159","186","187","188"]
        # prefix = random.choice(prelist)
        # number = str(random.randint(0,99999999)).zfill(8)
        # return prefix + number
        return self.faker.phone_number()

    def get_name(self):
        return self.faker.name()

    def get_id_num(self):
        return self.faker.ssn()

    def generate_bank_code(self,bank_name=None):
        # if BaseUtils.object_is_notnull(bank_name):
        #     bank_info = self.dao.get_bank_info(bank_name,'card')
        # else:
        #     bank_info = self.dao.get_card_zone(id,'card')
        #bank_code_length = bank_info.card_zone_length
        id = random.randint(0,2)
        bank_code_length =19
        #bank_code_bin = bank_info.card_zone_code
        bank_code_bin = ['622846',
                        '622200',
                        '622280'
                         ]
        width = bank_code_length-len(bank_code_bin[id])-1
        max_string = '9999999999999'
        max = int(max_string[0:width])
        random_code = str(random.randint(0,max)).zfill(width)
        bank_code = str(bank_code_bin[id])+random_code
        return self.get_bankcode_checkbit(bank_code)


    def get_bankcode_checkbit(self,bank_code):
        index_count =0
        find_count=0
        for i in range(int(len(bank_code)/2)):
            index = 2 * i
            find = 2 * i +1
            temp = str(int(bank_code[index]) * 2)
            if len(temp)==2:
                index_count = index_count + int(temp[0]) +int(temp[1])
            else:
                index_count = index_count +int(temp[0])
            if find <= len(bank_code):
                find_count = int(bank_code[find])+find_count
        check_bit = int(str(find_count + index_count)[-1])
        if check_bit==0:
            return bank_code+'0'
        else:
            check_bit = abs(check_bit -10)
            return bank_code + str(check_bit)

