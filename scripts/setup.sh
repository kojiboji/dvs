sudo mkdir -v -p /usr/local/aws
cd /usr/local/aws
sudo curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
sudo unzip awscliv2.zip
sudo ./aws/install
sudo rm awscliv2.zip

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

cd ~
sudo yum install git -y
git clone https://github.com/kojiboji/dvs.git