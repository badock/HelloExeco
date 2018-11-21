#!/usb/bin/env bash

apt update
apt install -y openjdk-8-jdk
apt install -y maven
apt install -y git

if [ ! -d HelloAkka ];then
    git clone https://github.com/badock/HelloAkka.git
fi

pushd HelloAkka
git pull
mvn compile
popd

exit 0