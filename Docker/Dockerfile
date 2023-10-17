FROM --platform=linux/amd64 ubuntu:20.04

ENV DEBIAN_FRONTEND noninteractive

# set default java environment variable
ENV JAVA_VERSION_MAJOR=8 \
    JAVA_VERSION_MINOR=111 \
    JAVA_HOME=/usr/lib/jvm/default-jvm \
    PATH=${PATH}:/usr/lib/jvm/default-jvm/bin/

RUN apt-get update && \ 
    apt-get upgrade -y && \
    apt install openjdk-11-jdk -yq && \
    apt install openjdk-17-jdk -yq 

RUN apt-get update && \ 
    apt install openjdk-8-jdk -yq && \
    ln -s /usr/lib/jvm/java-8-openjdk-amd64 /usr/lib/jvm/default-jvm && \
    apt-get clean all

# Check Java version
RUN java -version && \
    javac -version

# Install linux packages
RUN apt-get update
RUN apt-get -qq -y install software-properties-common git curl build-essential subversion perl wget unzip vim bc 

RUN apt-get install maven -yq

# Setup Apache Maven
ENV MAVEN_OPTS="-Xms256m -Xmx2048m"

# Check Maven version
RUN mvn -version

# Install Python
RUN add-apt-repository -y ppa:deadsnakes/ppa
RUN apt-get update
RUN apt-get install -y --no-install-recommends python3.9 python3.9-dev python3-pip python3-setuptools python3-wheel gcc
RUN python3.9 -m pip install pip --upgrade

RUN echo 'alias python=python3.9' >> /root/.bashrc

# RUN apt-get install pkg-config
# RUN apt-get install libcairo2-dev -yq

# RUN pip install argparse
# RUN pip freeze > requirements.txt
# RUN pip install -r requirements.txt

WORKDIR /root

ENV FRAMEWORK_HOME="/root/framework"

COPY vimrc .vimrc
ENV JAVA_TOOL_OPTIONS="-Dfile.encoding=UTF8"
ENV TMP_DIR="/tmp"

ENV PYTHONIOENCODING=utf-8

# install Maven 3.8.1
RUN wget https://archive.apache.org/dist/maven/maven-3/3.8.1/binaries/apache-maven-3.8.1-bin.tar.gz -P /tmp 
RUN tar -xzvf /tmp/apache-maven-3.8.1-bin.tar.gz -C /opt

# install Maven 3.8.6
RUN wget https://archive.apache.org/dist/maven/maven-3/3.8.6/binaries/apache-maven-3.8.6-bin.tar.gz -P /tmp
RUN tar -xzvf /tmp/apache-maven-3.8.6-bin.tar.gz -C /opt

# install gradle
RUN git config --global --add safe.directory '*'

# install python libraries
COPY requirements.txt /tmp/requirements.txt
RUN python3.9 -m pip install -r /tmp/requirements.txt

WORKDIR /root/framework
