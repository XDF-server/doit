# *-* coding:utf-8 *-*

import os
import ConfigParser

cf = ConfigParser.ConfigParser()
cf.read('../config.ini')
pipe_file = cf.get('QUEUE','PIPE_FILE')

wp = os.open(pipe_file,os.O_NONBLOCK | os.O_CREAT | os.O_RDWR)

os.write(wp,"kill()")
os.close(wp)
