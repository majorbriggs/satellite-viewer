echo "export LC_ALL=C" >> ~/.bashrc
source ~/.bashrc
apt update
apt upgrade -y
apt install -y python3-pip
apt install -y virtualenv
apt install -y libgdal-dev
apt install -y gdal-bin