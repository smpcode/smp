FROM python:3.7.3


WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./cli.py", "-f", "./conf/dev/conf.yml", "--route=all", "--port=7654", "--prefork=1", "-D", "--allow-origin=http://127.0.0.1:8081"]
