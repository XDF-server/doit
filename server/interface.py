# *-* coding:utf-8 *-*

import time
import os
import signal

from base import Configer
from design_model import singleton
from thread_pool import ThreadPool

@singleton
class Interface(object):
	
	def __init__(self):
			
		self._read_config()
		self._init_threadpool()
		self._get_pid()

	def _read_config(self):

		configer = Configer()
 		self.queue_size = configer.get_configer('QUEUE','queue_size')
                self.thread_pool_num = configer.get_configer('THREADPOOL','num')
	
	def _init_threadpool(self):	

		self.pool = ThreadPool(int(self.thread_pool_num),int(self.queue_size))

	def _get_pid(self):
		
		self.pid = os.getpid()

	def write(self,string):

		print string

	def transcode(self,string):

		self.pool.add_job(self._transcode,string)
		#通知idc_api转码完成

	def _transcode(self,filepath):
		
		print filepath
		time.sleep(100)
		print 'ok'

	def kill(self):
		os.kill(self.pid,signal.SIGKILL)

	def __getattribute__(self,name):
		
		try:
			res = object.__getattribute__(self,name)

		except:
			res = None	

		return res
