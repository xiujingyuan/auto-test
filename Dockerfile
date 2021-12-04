#FROM auto-python
#COPY requirements.txt ./
#RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
#COPY . /data/www/wwwroot/

FROM auto-python
#COPY init.sh /data/www/
# RUN pip install gunicorn
#COPY supervisord.conf /etc/supervisor/
#RUN mkdir -p /etc/supervisor/conf.d/
#RUN rm -rf /usr/local/lib/python3.7/site-packages/flask_script/__init__.py
#COPY __init__.py /usr/local/lib/python3.7/site-packages/flask_script/
CMD [ "sh", "/data/www/init.sh" ]
