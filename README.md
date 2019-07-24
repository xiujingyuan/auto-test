 **1.项目初始化**
 ##### db同步，创建数据库表
 ##### 执行命令：venv/bin/python3.7 manage.py db upgrade
 
 **2.本地运行项目**
 #### venv/bin/python gaea.py runserver --port 5003

 **3.Celery任务项目运行**
 #### venv/bin/celery worker -A celery_worker.celery --loglevel=info
