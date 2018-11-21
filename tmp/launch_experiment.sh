#!/usb/bin/env bash

cd HelloAkka

mvn exec:java -Dexec.mainClass=distributed.Main -Dexec.args="client ecotype-9.nantes.grid5000.fr 1234 ecotype-8.nantes.grid5000.fr 1234" | tee $HOME/output.log &

cd ..

sleep 60

exit 0