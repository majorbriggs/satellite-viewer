export LC_ALL=C
sudo apt install python-pip
if [ ! -d venv ]; then
    virtualenv -p python3 venv
fi
. venv/bin/activate
pip install numpy
pip install -r requirements.txt