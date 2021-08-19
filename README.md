**1.生成对应表的orm地址**
#### venv/bin/flask-sqlacodegen  --outfile=app/model/MockConfigDb.py --table=mock_config  mysql://root:Coh8Beyiusa7@127.0.0.1:3306/auto-test --flask
#### venv/bin/flask-sqlacodegen  --outfile=app/program_business/china/repay/model/AssetExtendDb.py --table=asset_extend  mysql://root:Coh8Beyiusa7@127.0.0.1:3306/rbiz3 --flask
#### flask-sqlacodegen  --outfile=app/program_business/china/biz_central/Model.py --table=capital_transaction,asset,asset_tran,central_sendmsg,central_task,capital_notify,central_synctask,capital_settlement_detail,capital_asset mysql://root:Coh8Beyiusa7@127.0.0.1:3306/biz2 --flask
