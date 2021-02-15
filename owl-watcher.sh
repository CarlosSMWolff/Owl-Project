#!/bin/bash

export DISPLAY=:0
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/games:/usr/local/games:/snap/bin
python3 /home/carlos/Owl-Project/owl-watcher.py >> /home/carlos/Owl-Project/Logs/log-owl.txt
