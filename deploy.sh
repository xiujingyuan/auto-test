echo "#########################修改系统配置##########################"
ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
# pip3 install elasticsearch redis

echo "#########################修改supervisor配置##########################"
cd /var/run
touch supervisor.sock
chmod 700 supervisor.sock
pwd
ls -al
sleep 1

echo "#########################拉取代码##########################"
#mkdir -p /data/www/wwwroot
cd /data/www/wwwroot
#git clone https://jc_mock:1LqUuzYMJXUS_io7Ab9q@git.kuainiujinke.com/cd-test/auto-test.git
#sleep 1

echo "#########################修改一些配置 auto-vue ##########################"
cp -f /data/www/wwwroot/auto-test/auto_test.conf /etc/supervisor/conf.d/auto_test.conf
mkdir -p /data/www/wwwroot/auto-test/logs/supervisor
mkdir -p /data/www/wwwroot/auto-test/logs/gunicon
touch /data/www/wwwroot/auto-test/logs/gunicon/access.log
touch /data/www/wwwroot/auto-test/logs/gunicon/info.log
touch /data/www/wwwroot/auto-test/logs/gunicon/gunicorn.log
touch /data/www/wwwroot/auto-test/logs/gunicon/gunicorn.pid
touch /data/www/wwwroot/auto-test/logs/supervisor/auto_test.log

echo "#########################修改一些配置 framework-test ##########################"
cp -f /data/www/wwwroot/framework-test/framework.conf /etc/supervisor/conf.d/framework.conf
mkdir -p /data/www/wwwroot/framework-test/logs/supervisor
mkdir -p /data/www/wwwroot/framework-test/logs/gunicon

echo "#########################修改一些配置 jc-mock ##########################"
cp -f /data/www/wwwroot/jc-mock/jc-mock.conf /etc/supervisor/conf.d/jc-mock.conf
cp -f /data/www/wwwroot/jc-mock/environment/k8s/config.py /data/www/wwwroot/jc-mock/app/common/config/config.py
mkdir -p /data/www/wwwroot/jc-mock/logs/supervisor
mkdir -p /data/www/wwwroot/jc-mock/logs/gunicon
mkdir -p /data/www/wwwroot/jc-mock/logs/celery
touch /data/www/wwwroot/jc-mock/logs/gunicon/access.log
touch /data/www/wwwroot/jc-mock/logs/gunicon/info.log
touch /data/www/wwwroot/jc-mock/logs/gunicon/gunicorn.log
touch /data/www/wwwroot/jc-mock/logs/gunicon/gunicorn.pid
sleep 1

echo "#########################启动web服务##########################"
supervisord -c /etc/supervisor/supervisord.conf
sleep 10
ps -fe

echo "#########################启动nginx务##########################"
nginx

echo "#########################查看日志##########################"
tail -F /data/www/wwwroot/auto-test/logs/supervisor/auto_test.log

