#!/bin/bash
echo 'KERNEL=="ttyUSB0", OWNER="root",GROUP ="root" ,MODE="0666"'>my-ttyUSB.rules
mv my-ttyUSB.rules /etc/udev/rules.d/my-ttyUSB.rules
