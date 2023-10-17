wget https://archive.apache.org/dist/maven/maven-3/3.8.6/binaries/apache-maven-3.8.6-bin.tar.gz -P /tmp # for running projects in GHRB benchmark
tar -xzvf /tmp/apache-maven-3.8.6-bin.tar.gz -C /opt
git config --global --add safe.directory '*'
export PATH=/opt/apache-maven-3.8.6/bin:$PATH