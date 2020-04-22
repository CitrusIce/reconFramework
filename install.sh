#!/bin/bash
cd tools
echo "installing oneforall"
#git clone https://github.com/shmilylty/OneForAll.git/
git clone https://gitee.com/shmilylty/OneForAll.git
python3.8 -m pip install -r OneForAll/requirements.txt

echo "installing dirsearch"
git clone https://github.com/maurosoria/dirsearch.git

echo "installing eyewitness"
git clone https://github.com/FortyNorthSecurity/EyeWitness.git
sudo bash EyeWitness/Python/setup/setup.sh

cd ..
python3 -m pip install -r requirements.txt