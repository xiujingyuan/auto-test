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
mkdir -p /data/www/wwwroot
cd /data/www/wwwroot
git clone git@git.kuainiujinke.com:cd-test/auto-test.git
sleep 1

echo "#########################修改一些配置##########################"
cp -f /data/www/wwwroot/auto-test/auto-test.conf /etc/supervisor/conf.d/auto_test.conf
mkdir -p /data/www/wwwroot/auto-test/logs/supervisor
mkdir -p /data/www/wwwroot/auto-test/logs/gunicon
sleep 1

echo "#########################启动web服务##########################"
supervisord -c /etc/supervisor/supervisord.conf
sleep 10
ps -fe


echo "#########################查看日志##########################"
tail -F /data/www/wwwroot/auto-test/logs/framework_test.log

