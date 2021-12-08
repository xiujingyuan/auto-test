#FROM auto-python
#COPY requirements.txt ./
#RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
#COPY . /data/www/wwwroot/

FROM auto-python:v2
COPY nginx.conf /usr/local/nginx/conf/nginx.conf
EXPOSE 80
STOPSIGNAL SIGQUIT
RUN addgroup --system --gid 102 nginx && adduser --system --disabled-login --ingroup nginx --no-create-home --home /nonexistent --gecos "nginx user" --shell /bin/false --uid 102 nginx
CMD ["nginx", "-g", "daemon off;"]
#COPY nginx-1.13.7.tar.gz .
#RUN tar -xf nginx-1.13.7.tar.gz
#RUN cd nginx-1.13.7
# COPY ngx_user.c /nginx-1.13.7/src/os/unix/ngx_user.c

#RUN cd nginx-1.13.7 && ./configure --prefix=/usr/local/nginx
#COPY objs/* /nginx-1.13.7/objs/
#COPY Makefile /nginx-1.13.7/Makefile

#RUN mkdir -p /var/log/nginx/
#RUN touch /var/log/nginx/error.log
#RUN mkdir -p /var/run/
#RUN touch /var/run/nginx.pid
#RUN mkdir -p /data/www/wwwroot/html/
#RUN mkdir -p /usr/local/nginx/conf/conf.d
#RUN cd nginx-1.13.7 && make install
#RUN ln -s /usr/local/nginx/sbin/nginx /usr/bin/nginx
#RUN rm -rf nginx-1.13.7
#RUN rm -rf nginx-1.13.7.tar.gz
#COPY init.sh /data/www/
# RUN pip install gunicorn
#COPY supervisord.conf /etc/supervisor/
#RUN mkdir -p /etc/supervisor/conf.d/
#RUN rm -rf /usr/local/lib/python3.7/site-packages/flask_script/__init__.py
#COPY __init__.py /usr/local/lib/python3.7/site-packages/flask_script/
