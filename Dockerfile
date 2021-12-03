#FROM auto-python
#COPY requirements.txt ./
#RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
#COPY . /data/www/wwwroot/

FROM auto-python
COPY init.sh /data/www/
RUN pip install supervisor

