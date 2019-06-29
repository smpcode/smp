FROM centos:centos7.2.1511

RUN yum install -y epel-release \
	&& yum install -y https://centos7.iuscommunity.org/ius-release.rpm \
	&& yum install -y python36u \
	&& yum -y install python36u-pip

RUN rpm --rebuilddb && yum install -y gcc-c++ bzip2-devel mysql-devel snappy-devel libffi-devel python36u-devel

RUN mkdir -p /data/www/smp \
	&& mkdir -p /data/logs/smp

WORKDIR /data/www/smp

COPY requirements.txt ./

RUN pip3.6 install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT /bin/bash
