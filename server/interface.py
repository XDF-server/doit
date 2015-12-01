# *-* coding:utf-8 *-*

import re
import time
import os
import signal
#from jsonpath_rw import jsonpath,parse
from hashlib import md5
import urllib2

from base import Configer
from design_model import singleton
from thread_pool import ThreadPool
from qiniu_wrap import QiniuWrap
from mongo import Mongo
import pprint 
@singleton
class Interface(object):

	img_url_exp = re.compile(r'http://qdimg.okjiaoyu.cn/[\S\s]*')
	qiniu_prefix = 'http://%s.okjiaoyu.cn/%s'
	
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

	def local_img(self,string):
		from gl import LOG
		update_flag = False
		LOG.info('start local img,question id [%s]' % string)
		question_id = int(string)
		mongo = Mongo()
		mongo.connect('resource')
		mongo.select_collection('mongo_question_json')
		json = mongo.find_one({'question_id':question_id},{'content':1})
		mongo.select_collection('mongo_question_html')
		html = str(mongo.find_one({'question_id':question_id},{'content':1}))
		#img_expr = parse("content[*].*[*]")

		#img_list =  [match.value for match in img_expr.find(json) if isinstance(match.value,dict) and\
		#             'type' in match.value.keys() and match.value['type'] == 'image']

		#pprint.pprint(json)
		content = ''

		if json:
			content = json['content']

			for key,wrap in content.items():
				for idx,item in enumerate(content[key]):
					if isinstance(item,str):
						continue

					if isinstance(item,dict):
						if 'group' in item.keys():
							group = item['group']
							for index,item1 in enumerate(group):
								if isinstance(item1,dict) and 'type' in item1.keys() and item1['type'] == 'image':
									ori_url = item1['value']
									qiniu_url = self._upload_qiniu(ori_url)
									if qiniu_url:
										content[key][idx]['group'][index]['value'] = qiniu_url
										update_flag = True
										html = html.replace(ori_url,qiniu_url)


						if 'type' in item.keys() and item['type'] == 'image':
							ori_url = item['value']
							qiniu_url = self._upload_qiniu(ori_url)
							if qiniu_url:
								content[key][idx]['value'] = qiniu_url
								update_flag = True
								html = html.replace(ori_url,qiniu_url)

					if isinstance(item,list):
						for index,item1 in enumerate(item):
							if 'type' in item1.keys() and item1['type'] == 'image':
								ori_url = item1['value']
								qiniu_url = self._upload_qiniu(ori_url)
								
								if qiniu_url:
									content[key][idx][index]['value'] = qiniu_url
									update_flag = True
									html = html.replace(ori_url,qiniu_url)

		if update_flag:
                	mongo.select_collection('mongo_question_json')
			json_effected = mongo.update_many({'question_id':question_id},{'$set':{'content':content}})
			mongo.select_collection('mongo_question_html')
			html_effected = mongo.update_many({'question_id':question_id},{'$set':{'content':html}})
			LOG.info('mongo update successful json[%d] -- html[%d]' % (json_effected,html_effected))
			
	def _upload_qiniu(self,ori_url):
		from gl import LOG
		LOG.info('Original Image Url [%s]' % ori_url)
		if not self.img_url_exp.match(ori_url):
			suffix = ori_url[ori_url.rfind('.'):]	
			qiniu_file_name = md5(ori_url).hexdigest() + suffix
			
			request = urllib2.Request(ori_url)
			response = urllib2.urlopen(request)
			img_data =  response.read()

			#LOG.info('img data [%s]' % img_data)	

			qiniu = QiniuWrap()
			res = qiniu.upload_data('qdimg',qiniu_file_name,img_data)

			if not res:
				qiniu_url = self.qiniu_prefix % ('qdimg',qiniu_file_name)
				LOG.info('[%s] local [%s] successful' % (ori_url,qiniu_url))			
				return qiniu_url
			else:
				LOG.error('upload qiniu error [%s]' % res)
				return None

				

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
