cd /data/www/wwwroot
git clone git@git.kuainiujinke.com:cd-test/auto-test.git
cp /data/www/wwwroot/auto-test/deploy.sh /data/www/deploy.sh
cd /data/www
sleep 2
sh deploy.sh