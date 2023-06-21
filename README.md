**1.生成对应表的orm地址**
#### venv/bin/flask-sqlacodegen  --outfile=app/model/CaseTaskDb.py --table=case_task  mysql://root:Coh8Beyiusa7@127.0.0.1:3306/auto-test --flask
#### flask-sqlacodegen  --outfile=app/model/TraceInfoDb.py --table=trace_info  mysql://root:Coh8Beyiusa7@127.0.0.1:3306/trace_info --flask
####  
#### venv/bin/flask-sqlacodegen  --outfile=app/services/china/repay/AssetExtendDb.py --table=capital_settlement_detail  mysql://root:Coh8Beyiusa7@127.0.0.1:3306/biz3 --flask
#### flask-sqlacodegen  --outfile=app/program_business/china/biz_central/Model.py --table=capital_transaction,asset,asset_tran,central_sendmsg,central_task,capital_notify,central_synctask,capital_settlement_detail,capital_asset mysql://root:Coh8Beyiusa7@127.0.0.1:3306/biz2 --flask
#### flask-sqlacodegen  --outfile=app/program_business/china/biz_central/Model.py --table=capital_transaction,asset,asset_tran,central_sendmsg,central_task,capital_notify,central_synctask,withhold_history,withhold_result,holiday,capital_settlement_detail,capital_asset mysql://root:Coh8Beyiusa7@127.0.0.1:3306/biz4 --flask
#### flask-sqlacodegen  --outfile=app/program_business/china/biz_central/HolidayDb.py --table=holiday mysql://root:Coh8Beyiusa7@127.0.0.1:3306/biz2 --flask
#### flask-sqlacodegen  --outfile=app/services/china/clean/Model.py --table=clean_task,clean_clearing_trans,clean_capital_settlement_pending mysql://capital:piqXNdySXa2bLsbE@127.0.0.1:3321/capital7 --flask
#### flask-sqlacodegen  --outfile=app/services/china/grant/ContractModel.py mysql://root:Coh8Beyiusa7@127.0.0.1:3306/contract --flask

### flask-sqlacodegen  --outfile=app/program_business/china/biz_central/withhold_history.py --table=withhold_history mysql://root:Coh8Beyiusa7@127.0.0.1:3306/biz2 --flask

**2.放款source_type对应的资方类型**
# APR融担 -i https://pypi.tuna.tsinghua.edu.cn/simple/
#大单source_type=apr36
#融担小单source_type=rongdan
#支持资金方：
#哈密天邦新疆
#哈密天邦
#浩瀚汇通
#华北润乾
#龙江大秦
#墨智北银
#通融小贷
#微神马———（小单会分配tianbang/zhongyi等担保方，今后大单不分配了，大单的sub_order_type没有值了，小单才会有值）
#中科兰州

##IRR产品线
#无权益搭售（IRR权益无搭售）
#【仅大单,无小单】
#大单source_type=irr36
#支持的资金方：
#秦农天邦
#秦农杰益
#墨智金美信

#大单+融担小单 （目前无资方支持----用兰州来测，测完记得恢复数据）
#大单source_type=irr36
#融担小单source_type=rongdan_irr

#权益搭售
#大单+权益小单（IRR权益）
#大单source_type=irr36_quanyi
#权益小单source_type=lieyin    ———权益小单无RongdanAllocate任务
#支持的资金方：
#哈密天邦新疆
#哈密天邦
#浩瀚汇通
#华北润乾
#秦农天邦
#秦农杰益
#通融小贷
#墨智金美信


#大单+融担小单+权益小单
#大单source_type=irr36_quanyi
#融担小单source_type=rongdan_irr （这个场景的小单会使用大单计算出来的金额进件，放款成功通知内有金额）
#权益小单source_type=lieyin
#支持的资金方：
#龙江大秦
#中科兰州

# docker run -p 6868:6868 -d --name auto-test  auto-python

# docker build -t auto-python .
# cp mystifying_archimedes:/etc/nginx/nginx.conf .
# docker run -it auto-python /bin/bash

# docker exec -it auto-test /bin/bash

# docker container start auto-test