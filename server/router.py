# *-* coding:utf-8 *-*

import os
import re
import select
import threading

from base import Base,Configer
from interface import Interface

class Router(threading.Thread):
		
	def __init__(self,threadid,name):

		threading.Thread.__init__(self)
		self.threadid = threadid
		self.name = name
		
		self._read_config()
		self._init_pipe()
		self._init_pattern()

		self.interface_obj = Interface()

	def _read_config(self):

		configer = Configer()
		self.pipe_file = configer.get_configer('QUEUE','pipe_file')
		self.timeout = configer.get_configer('QUEUE','timeout')
		self.max_cmd = configer.get_configer('QUEUE','max_cmd')

	def _init_pipe(self):

		try:
			os.mkfifo(self.pipe_file)
		except:
			pass
	
		self.pipe_fd = os.open(self.pipe_file,os.O_RDWR)
		self.epoll = select.epoll()
		self.epoll.register(self.pipe_fd,select.EPOLLIN)

	def _init_pattern(self):
		
		self.FUNC_STR = re.compile(r"^([a-zA-Z_-]+)\(([\s\S]*)\)$")

	def run(self):

		while True:
			events = self.epoll.poll(int(self.timeout))
			
			for fd,event in events:
				if event & select.EPOLLIN:
					if fd == self.pipe_fd:
						msg = os.read(fd,int(self.max_cmd))
					
						(func_name,para) = self._parse(msg)

						if callable(getattr(self.interface_obj,func_name)):
							getattr(self.interface_obj,func_name)(para) if para else getattr(self.interface_obj,func_name)()
						else:
							pass
					else:
						continue

	def _parse(self,msg):
		
		m = self.FUNC_STR.match(msg)	

		if m:
			return m.group(1),m.group(2)
		else:
			pass

	def __del__(self):
		os.unlink(self.pipe_file)

