#!/usb/bin/env bash

mvn exec:java -Dexec.mainClass=distributed.Main -Dexec.args="server 1234" > output.log

exit 0