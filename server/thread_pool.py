# *-* coding:utf-8 *-*

import Queue
import threading
import time

class WorkThread(threading.Thread):
	
	def __init__(self,pool):

		threading.Thread.__init__(self)
		self.pool = pool
		self.start()

	def run(self):

		while True:
			self.pool.mutex_lock.acquire()
			while self.pool.task_queue.empty() and not self.pool.pool_close_flag:
				self.pool.queue_not_empty.wait()

			if self.pool.pool_close_flag:
				self.pool.mutex_lock.release()
				break

			func,argv = self.pool.task_queue.get(block = False)
			
			if self.pool.task_queue.empty():
				self.pool.queue_empty.notify()

			if self.pool.task_queue.qsize() < self.pool.max_task_num:
				self.pool.queue_not_full.notifyAll()
			
			self.pool.mutex_lock.release()

			func(argv)
			self.pool.task_queue.task_done()


class ThreadPool(object):
	
	def __init__(self,thread_num = 5,max_task_num = 10000):

		self.task_queue = Queue.Queue(maxsize = max_task_num)
		self.max_task_num = max_task_num
		self.threads = []
		self._init_thread_pool(thread_num)

	def _init_thread_pool(self,thread_num):

		self.pool_close_flag = False
		self.mutex_lock = threading.Lock()
		self.queue_empty = threading.Condition(self.mutex_lock)
		self.queue_not_empty = threading.Condition(self.mutex_lock)
		self.queue_not_full = threading.Condition(self.mutex_lock)

		for i in range(thread_num):
			self.threads.append(WorkThread(self))
		
	def add_job(self,func,argv):
		
		if not func and not argv:
			return -1
		
		self.mutex_lock.acquire()
		
		while self.task_queue.qsize() == self.max_task_num and self.pool_close_flag:
			self.queue_not_full.wait()
		
		if self.pool_close_flag:
			self.mutex_lock.release()
			return -2
		
		self.task_queue.put((func,argv))
		
		self.queue_not_empty.notifyAll()
		
		self.mutex_lock.release()

'''
def job(argv):
	print 'doing.......'
	time.sleep(10)
	print threading.current_thread(),list(argv)

if __name__ == '__main__':
	pool = ThreadPool()
	for i in range(20):
		str = 'this is job %d' % (i)
		pool.add_job(job,str)
'''

