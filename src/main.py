#!/usr/bin/python
import sys
from modules import consumer

configpath="./../conf/config.yml"

if __name__ == '__main__':
    starttime=sys.argv[1]
    endtime=sys.argv[2]
    consumer.run(configpath,starttime,endtime)
    