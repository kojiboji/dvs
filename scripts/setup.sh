sudo mkdir -v -p /usr/local/aws
cd /usr/local/aws
sudo curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
sudo unzip awscliv2.zip
sudo ./aws/install
sudo rm awscliv2.zip

#ffmpeg is only needed on the "driver"
sudo mkdir -v -p /usr/local/bin/ffmpeg
cd /usr/local/bin/ffmpeg
sudo wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-i686-static.tar.xz
sudo tar -v -xf ffmpeg-release-i686-static.tar.xz --strip-components=1
sudo rm -v -f ffmpeg-release-i686-static.tar.xz
sudo ln -snf /usr/local/bin/ffmpeg/ffmpeg /usr/bin/ffmpeg
sudo ln -snf /usr/local/bin/ffmpeg/ffprobe /usr/bin/ffprobe

sudo yum install java-11-amazon-corretto.x86_64 -y

sudo mkdir -v -p /usr/local/spark
cd /usr/local/spark
sudo wget https://dlcdn.apache.org/spark/spark-3.2.0/spark-3.2.0-bin-hadoop3.2.tgz
sudo tar -v -xf spark-3.2.0-bin-hadoop3.2.tgz
sudo rm -v -f spark-3.2.0-bin-hadoop3.2.tgz

echo "export JAVA_HOME=/usr/lib/jvm/java-11-amazon-corretto.x86_64" >> ~/.bashrc
echo "export SPARK_HOME=/usr/local/spark/spark-3.2.0-bin-hadoop3.2" >> ~/.bashrc
source ~/.bashrc

sudo ln $SPARK_HOME/bin/spark-submit /usr/bin/spark-submit
sudo ln $SPARK_HOME/sbin/start-master.sh /usr/bin/start-master
sudo ln $SPARK_HOME/sbin/start-worker.sh /usr/bin/start-worker

sudo ln $SPARK_HOME/sbin/stop-master.sh /usr/bin/stop-master
sudo ln $SPARK_HOME/sbin/stop-worker.sh /usr/bin/stop-worker

cd ~
sudo yum install git -y
git clone https://github.com/kojiboji/dvs.git


sudo yum install opencv -y


#install the right python
# install pre-requisites
sudo yum -y groupinstall development
sudo yum -y install zlib-devel
sudo yum -y install openssl-devel


# Installing openssl-devel alone seems to result in SSL errors in pip (see https://medium.com/@moreless/pip-complains-there-is-no-ssl-support-in-python-edbdce548852)
# Need to install OpenSSL also to avoid these errors
wget https://github.com/openssl/openssl/archive/OpenSSL_1_0_2l.tar.gz
tar -zxvf OpenSSL_1_0_2l.tar.gz
cd openssl-OpenSSL_1_0_2l/

./config shared
make
sudo make install
export LD_LIBRARY_PATH=/usr/local/ssl/lib/

cd ..
rm OpenSSL_1_0_2l.tar.gz
rm -rf openssl-OpenSSL_1_0_2l/


# Install Python 3.6.4
wget https://www.python.org/ftp/python/3.6.4/Python-3.6.4.tar.xz
tar xJf Python-3.6.4.tar.xz
cd Python-3.6.4

./configure
make
sudo make install

cd ..
rm Python-3.6.4.tar.xz
sudo rm -rf Python-3.6.4

cd ~/dvs
pip3 install --upgrade virtualenv
virtualenv --python=/usr/local/bin/python3 spark_env
source spark_env/bin/activate
pip3 install -r requirements.txt

echo "export PYSPARK_PYTHON=/home/ec2-user/dvs/spark_env/bin/python" >> ~/.bashrc
echo "export PYSPARK_DRIVER_PYTHON=/home/ec2-user/dvs/spark_env/bin/python" >> ~/.bashrc
source ~/.bashrc

#run 'aws configure' manually to give node access to the s3 buckets
#set SPARK_MASTER variable to something, eg 'spark://ip-172-31-1-6.us-west-1.compute.internal:7077'
