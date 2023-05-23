## About

This is Seaky's box of basic tools





fatal error: Python.h: No such file or directory

```
yum install gcc libffi-devel python3-devel openssl-devel -y
```



## Install

Centos7 install python3.7

```
yum install zlib-devel bzip2-devel openssl-devel ncurses-devel sqlite-devel readline-devel tk-devel gcc make libffi-devel

yum -y install epel-release 
yum install python3-pip
pip3 install --upgrade pip

wget https://www.python.org/ftp/python/3.7.0/Python-3.7.0.tgz
./configure prefix=/usr/local/python3 
make && make install
```



## Log

### 0.1

detached from seakylib



