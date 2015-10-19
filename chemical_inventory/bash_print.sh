#!/bin/bash
cd /srv/professor_oak/chemical_inventory/label_printing
glabels-3-batch --input=input.csv --output=output.pdf gLabelsTest.glabels
scp output.pdf pi@10.19.193.103:/home/pi/label_printing
ssh pi@10.19.193.103 /home/pi/label_printing/bash_print.sh